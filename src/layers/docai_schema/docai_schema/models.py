import json
from enum import StrEnum
from typing import Any

from aws_lambda_powertools.utilities.parser import BaseModel, Field, validator
from jsonschema import Draft202012Validator as Validator

from docai_schema import exceptions as exc
from docai_schema import utils

TOKEN_LIMIT = 2048


class SchemaStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class SchemaModel(BaseModel):
    schema_name: str
    schema_description: str
    schema_definition: dict[str, Any]
    schema_version: str | None = Field(default_factory=utils.guid)
    schema_status: SchemaStatus = Field(default=SchemaStatus.ACTIVE)
    number_of_tokens: int | None = None

    @validator("schema_definition")
    def validate_schema_definition(cls, v: dict[str, Any]) -> dict[str, Any]:
        Validator.check_schema(v)
        return v

    @validator("number_of_tokens", always=True)
    def validate_number_of_tokens(cls, v: int | None, values: dict[str, Any]) -> int:
        value = json.dumps(values["schema_definition"])
        number_of_tokens = utils.count_tokens(value)
        if number_of_tokens > TOKEN_LIMIT:
            raise exc.SchemaDefinitionTooLarge(
                f"Schema definition is too large "
                f"(i.e. limit {TOKEN_LIMIT}). Number of "
                f"tokens: {number_of_tokens}"
            )
        return number_of_tokens
