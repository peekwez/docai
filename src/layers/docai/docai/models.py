import json
from datetime import datetime
from enum import StrEnum
from typing import Any

from aws_lambda_powertools.utilities.parser import BaseModel, Field, validator
from jsonschema import Draft202012Validator as JSONValidator

from docai import constants as c
from docai import exceptions as exc
from docai import utils

TOKEN_LIMIT = 2048


def utcnow():
    return datetime.utcnow().isoformat()


class ErrorModel(BaseModel):
    name: str
    message: str


class ErrorResponseModel(BaseModel):
    OK: bool = Field(default=False)
    error: ErrorModel


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


def is_image(mime_type: str) -> bool:
    """Check if mime type is an image"""
    return mime_type in (
        MimeTypeEnum.PNG.value,
        MimeTypeEnum.JPG.value,
        MimeTypeEnum.JPEG.value,
        MimeTypeEnum.GIF.value,
        MimeTypeEnum.BMP.value,
        MimeTypeEnum.TIFF.value,
    )


def is_pdf(mime_type: str) -> bool:
    """Check if mime type is a PDF"""
    return mime_type == MimeTypeEnum.PDF.value


def is_text(mime_type: str) -> bool:
    """Check if mime type is a PDF"""
    return mime_type == MimeTypeEnum.TXT.value


class DocumentModel(BaseModel):
    content: str
    mime_type: MimeTypeEnum

    def is_text(self) -> bool:
        return is_text(self.mime_type)

    def is_image(self) -> bool:
        return is_image(self.mime_type)

    def is_pdf(self) -> bool:
        return is_pdf(self.mime_type)


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
