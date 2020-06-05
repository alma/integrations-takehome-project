from enum import Enum

from flask import jsonify


class ErrorCode(Enum):
    INVALID_VALUE = "invalid_value"
    MISSING_FIELD = "missing_field"
    NOT_FOUND = "not_found"


class ValidationError(Exception):
    def __init__(self, field: str, error_code: Enum):
        self.field = field
        self.error_code = error_code

    @property
    def http_response(self):
        response = jsonify(
            {"error": {"field": self.field, "code": self.error_code.value}}
        )
        response.status_code = 400
        return response


class NotFoundError(Exception):
    pass
