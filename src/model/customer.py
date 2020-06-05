from . import Model


class Customer(Model):
    FIELD_TYPES = {"first_name": str, "last_name": str, "email": str, "phone": str}
