import math
from datetime import datetime
from typing import List

# Mock fee plans and eligibility amount constraints
import pytz
from dateutil.relativedelta import relativedelta

PLANS = {
    3: {"min": 10000, "max": 200000, "fees": 180},
    4: {"min": 20000, "max": 200000, "fees": 210},
}


class Payment:
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
        pass
