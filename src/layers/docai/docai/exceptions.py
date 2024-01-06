from aws_lambda_powertools.utilities.parser import ValidationError

from docai import constants as c


class SchemaDefinitionTooLarge(Exception):
    def __init__(
        self,
        message=f"Schema definition is too large. Max tokens {c.SCHEMA_TOKEN_LIMIT}",
    ):
        super().__init__(message)


class SchemaDoesNotExist(Exception):
    def __init__(self, message="Schema does not exist."):
        super().__init__(message)


class InvalidMimeType(Exception):
    def __init__(self, message="Invalid MIME type."):
        super().__init__(message)


class InvalidData(Exception):
    def __init__(self, message="Invalid data."):
        super().__init__(message)


class RequestDoesNotExist(Exception):
    def __init__(self, message="Request does not exist."):
        super().__init__(message)


EXCEPTIONS = (
    InvalidData,
    InvalidMimeType,
    ValidationError,
    RequestDoesNotExist,
    SchemaDoesNotExist,
    SchemaDefinitionTooLarge,
)
