from . import Model


class Address(Model):
    FIELD_TYPES = {"line1": str, "postal_code": str, "city": str}


# shameful hack 🙈 (so that validation errors show the right name...)
Address.__name__ = "shipping_address"
