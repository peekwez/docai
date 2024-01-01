import base64
import io
import json
import os
import random
import re
import string

import boto3
import tiktoken
from jsonschema import Draft202012Validator as Validator
from pdf2image import convert_from_bytes

from docai import constants as c
from docai import exceptions as exc

alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
tokenizer = tiktoken.get_encoding("cl100k_base")


def guid(length: int = 10) -> str:
    """Generate a random string of fixed length"""
    return "".join(random.choices(alphabet, k=length))


def encode(string: str) -> list[int]:
    """Encode a string into tokens"""
    return tokenizer.encode(string)


def decode(tokens: list[int]) -> str:
    """Decode tokens into a string"""
    return tokenizer.decode(tokens)


def count_tokens(string: str) -> int:
    """Count the number of tokens in a string"""
    return len(encode(string))


def load_pdf(data: str) -> list[str]:
    """Given a base64 encoded string, return the contents of document into multiple images"""
    decoded = base64.b64decode(data)
    pages = convert_from_bytes(decoded, 300, thread_count=6)
    images = []
    for page in pages:
        fp = io.BytesIO()
        page.save(fp, format="JPEG")
        base64_data = base64.b64encode(fp.getvalue()).decode("utf-8")
        images.append(f"data:image/jpeg;base64,{base64_data}")
    return images


def load_image(data: str) -> list[str]:
    """Given a base64 encoded string, return the contents of the image as a list of base64 string."""
    return [data]


def validate_data(data_object: str, schema_definition: dict) -> dict:
    """Given a JSON string, and a schema definition return a validated JSON data."""
    match = re.search(
        r"\{.*\}", data_object.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    output = ""
    if match:
        output = match.group()
    data = json.loads(output, strict=False)

    try:
        Validator(schema_definition).validate(data)
    except Exception:
        raise exc.InvalidData("Data does not match schema")
    return data


class Config:
    def __init__(self):
        self.__ssm = boto3.client("ssm")
        self.__sm = boto3.client("secretsmanager")

    def get_parameter(self, name: str) -> str:
        """Get a parameter from SSM"""
        return self.__ssm.get_parameter(Name=f"/{c.STAGE}" + name)["Parameter"]["Value"]

    def get_secret(self, name: str) -> str:
        """Get a secret from Secrets Manager"""
        return self.__sm.get_secret_value(SecretId=name)["SecretString"]


class Resource:
    def __init__(self):
        self.__session = boto3.Session()
        self.__config = Config()

    def get_table(self, parameter_name: str) -> boto3.resource:
        """Get a DynamoDB table resource"""
        table_name = self.__config.get_parameter(parameter_name)
        return self.__session.resource("dynamodb").Table(table_name)
