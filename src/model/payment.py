import math
from datetime import datetime
from enum import Enum
from os import environ
from typing import List

# Mock fee plans and eligibility amount constraints
import pytz
from dateutil.relativedelta import relativedelta

from .address import Address
from ..lib.errors import ValidationError, ErrorCode
from . import Model

PLANS = {
    3: {"min": 10000, "max": 200000, "fees": 180},
    4: {"min": 20000, "max": 200000, "fees": 210},
}


class PaymentState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"


class Payment(Model):
    FIELD_TYPES = {
        "purchase_amount": int,
        "installments_count": int,
        "return_url": str,
    }

    @classmethod
    def is_eligible(cls, purchase_amount: int, installments_count: int) -> bool:
        if installments_count not in PLANS:
            return False

        min = PLANS[installments_count]["min"]
        max = PLANS[installments_count]["max"]

        return min <= purchase_amount <= max

    @classmethod
    def fees_for(cls, installments_count: int) -> int:
        if installments_count not in PLANS:
            return 0

        return PLANS[installments_count]["fees"]

    @classmethod
    def constraints_for(cls, installments_count: int) -> dict:
        if installments_count not in PLANS:
            return {"installments_count": {"minimum": 3, "maximum": 4}}

        return {
            "purchase_amount": {
                "minimum": PLANS[installments_count]["min"],
                "maximum": PLANS[installments_count]["max"],
            }
        }

    @classmethod
    def compute_installments(
        cls, purchase_amount: int, installments_count: int
    ) -> List[dict]:
        if installments_count not in PLANS:
            return []

        today = datetime.now(pytz.utc)

        alpha = 1 / installments_count

        # Computed first installment after next installments to make sure sum == purchase_amount
        after = math.floor(purchase_amount * (1 - alpha) / (installments_count - 1))
        first = purchase_amount - ((installments_count - 1) * after)
        phasing = [first] + [after] * (installments_count - 1)

        fees = PLANS[installments_count]["fees"]

        # Put all fees on first installment:
        installments = [
            {
                "due_date": int(today.timestamp()),
                "net_amount": phasing[0],
                "customer_fee": fees,
            }
        ]

        # Compute dates of future installments
        due_dates = [
            today + relativedelta(months=k) for k in range(1, installments_count)
        ]
        for k, due_date in enumerate(due_dates):
            installments.append(
                {
                    "due_date": int(due_date.timestamp()),
                    "net_amount": phasing[k + 1],
                    "customer_fee": 0,
                }
            )

        return installments

    def __init__(self, data: dict):
        self.customer = None
        self.state = PaymentState.NOT_STARTED

        super(Payment, self).__init__(data)

        if "shipping_address" not in data:
            raise ValidationError("payment.shipping_address", ErrorCode.MISSING_FIELD)

        self.shipping_address = Address(data["shipping_address"])

        if not Payment.is_eligible(self.purchase_amount, self.installments_count):
            raise ValidationError("payment.installments_count", ErrorCode.INVALID_VALUE)

        self.installments = Payment.compute_installments(
            self.purchase_amount, self.installments_count
        )

    def to_dict(self) -> dict:
        return {
            "url": f"http://0.0.0.0:{environ.get('PORT', '5000')}/pp/{self.id}",
            "installments": self.installments,
            "shipping_address": self.shipping_address.to_dict(),
            "customer": self.customer.to_dict(),
            "state": self.state.value,
            **super(Payment, self).to_dict(),
        }
