import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from aws_lambda_powertools.utilities.parser import BaseModel, Field, validator
from jsonschema import Draft202012Validator as JSONValidator

from docai import constants as c
from docai import exceptions as exc
from docai import utils

TOKEN_LIMIT = 2048


def utcnow():
    return datetime.utcnow().isoformat()


class ErrorModel(BaseModel):
    error_name: str
    error_message: str


class ResultResponseModel(BaseModel):
    OK: Literal[True] = True
    result: dict


class ErrorResponseModel(BaseModel):
    OK: Literal[False] = False
    error: ErrorModel

    def log_dict(self) -> dict:
        return self.error.dict()


class SchemaStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class MimeTypeEnum(StrEnum):
    TXT = "text/plain"
    PDF = "application/pdf"
    PNG = "image/png"
    JPG = "image/jpg"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    WEBP = "image/webp"


class SchemaModel(BaseModel):
    schema_name: str
    schema_description: str
    schema_definition: dict[str, Any]
    schema_version: str | None = Field(default_factory=utils.guid)
    schema_status: SchemaStatus = Field(default=SchemaStatus.ACTIVE)
    number_of_tokens: int | None = None
    created_at: str = Field(default_factory=utcnow)

    @validator("schema_definition")
    def validate_schema_definition(cls, v: dict[str, Any]) -> dict[str, Any]:
        JSONValidator.check_schema(v)
        return v

    @validator("number_of_tokens", always=True)
    def validate_number_of_tokens(cls, v: int | None, values: dict[str, Any]) -> int:
        if v is not None:
            return v
        value = json.dumps(values["schema_definition"])
        number_of_tokens = utils.count_tokens(value)
        if number_of_tokens > c.SCHEMA_TOKEN_LIMIT:
            raise exc.SchemaDefinitionTooLarge(
                f"Schema definition is too large "
                f"(i.e. limit {TOKEN_LIMIT}). Number of "
                f"tokens: {number_of_tokens}"
            )
        return number_of_tokens
