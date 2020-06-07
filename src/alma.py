from flask import Flask, request, jsonify, render_template, redirect

from .lib.errors import ValidationError, ErrorCode, NotFoundError
from .lib.jinja import configure_jinja_env
from .model.customer import Customer
from .model.payment import Payment, PaymentState

app = Flask(__name__)
configure_jinja_env(app.jinja_env)

# No DB required... just store payments in memory
PAYMENTS = {}


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return e.http_response


@app.errorhandler(NotFoundError)
@app.errorhandler(404)
def handle_404(e):
    resp = jsonify(error={"code": ErrorCode.NOT_FOUND.value})
    resp.status_code = 404
    return resp


@app.after_request
def add_cors_headers(response):
    # To make things simple, always allow any origin to call this API
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Authorization, Content-Type, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"

    return response


@app.route("/")
def hello_world():
    return (
        "See "
        '<a href="https://github.com/alma/integrations-takehome-project#endpoints-disponibles">here</a> '
        "for endpoints documentation"
    )


@app.route("/payments/eligibility", methods=["POST"])
def check_eligibility():
    data = request.get_json(force=True)

    if "payment" not in data:
        raise ValidationError("payment", ErrorCode.MISSING_FIELD)

    payment_data = data["payment"]
    for field in ("purchase_amount", "installments_counts"):
        if field not in payment_data:
            raise ValidationError(f"payment.{field}", ErrorCode.MISSING_FIELD)

    purchase_amount = payment_data["purchase_amount"]
    if not isinstance(purchase_amount, int):
        raise ValidationError(
            f"payment.purchase_amount", ErrorCode.INVALID_VALUE,
        )

    response = []
    installments_counts = payment_data["installments_counts"]
    if not isinstance(installments_counts, list):
        raise ValidationError(
            f"payment.installments_counts", ErrorCode.INVALID_VALUE,
        )

    for installments_count in installments_counts:
        if not isinstance(installments_count, int):
            raise ValidationError(
                f"payment.installments_counts.{installments_count}",
                ErrorCode.INVALID_VALUE,
            )

        eligibility = {"installments_count": installments_count}

        if Payment.is_eligible(purchase_amount, installments_count):
            eligibility.update(
                {
                    "eligible": True,
                    "installments": Payment.compute_installments(
                        purchase_amount, installments_count
                    ),
                }
            )
        else:
            eligibility.update(
                {
                    "eligible": False,
                    "constraints": Payment.constraints_for(installments_count),
                }
            )

        response.append(eligibility)

    return jsonify(response)


@app.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json(force=True)

    if "payment" not in data:
        raise ValidationError("payment", ErrorCode.MISSING_FIELD)

    payment = Payment(data["payment"])

    if "customer" not in data:
        raise ValidationError("customer", ErrorCode.MISSING_FIELD)

    payment.customer = Customer(data["customer"])

    # Store newly created payment in memory
    PAYMENTS[payment.id] = payment

    return jsonify(payment.to_dict())


@app.route("/payments/<payment_id>", methods=["GET"])
def get_payment(payment_id):
    if payment_id not in PAYMENTS:
        raise NotFoundError()

    return jsonify(PAYMENTS[payment_id].to_dict())


@app.route("/pp/<payment_id>", methods=["GET"])
def payment_page(payment_id):
    if payment_id not in PAYMENTS:
        raise NotFoundError()

    return render_template("payment_page.html.j2", payment=PAYMENTS[payment_id])


@app.route("/pp/<payment_id>/pay", methods=["POST"])
def charge_payment(payment_id):
    if payment_id not in PAYMENTS:
        raise NotFoundError()

    # We don't care about the actual card data that may be passed in.
    # Just mark the payment as being started, and redirect to the return url
    payment = PAYMENTS[payment_id]
    payment.state = PaymentState.IN_PROGRESS

    return redirect(payment.redirect_url)
