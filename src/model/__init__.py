from uuid import uuid4

from ..lib.errors import ErrorCode, ValidationError


class Model:
    FIELD_TYPES = {}

    def __init__(self, data):
        for field in self.FIELD_TYPES.keys():
            if field not in data:
                raise ValidationError(
                    f"{self.__class__.__name__.lower()}.{field}",
                    ErrorCode.MISSING_FIELD,
                )

            value = data[field]
            if type(value) != self.FIELD_TYPES[field]:
                raise ValidationError(f"payment.{field}", ErrorCode.INVALID_VALUE)

            if type(value) == str and value.strip() == "":
                raise ValidationError(f"payment.{field}", ErrorCode.INVALID_VALUE)

            self.__setattr__(field, value)

        self.id = uuid4()

    def to_dict(self):
        return {
            "id": self.id,
            **{f: self.__getattribute__(f) for f in self.__class__.FIELD_TYPES.keys()},
        }
