import os
from collections import namedtuple
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_lambda as _lambda

Params = namedtuple(
    "Params",
    [
        "http_method",
        "http_path",
        "function_name",
        "function_path",
        "service",
        "namespace",
    ],
)

STAGE = os.environ.get("STAGE", "dev")
ROOT_PATH = Path(__file__).parent.parent.parent
LAYERS_ROOT = ROOT_PATH / "src/layers"
FUNCTIONS_ROOT = ROOT_PATH / "src/functions"

BUNDLE_COMMAND = (
    "pip install -r requirements.txt -t "
    "/asset-output/python && "
    "cp -a docai /asset-output/python"
)

LAMBDA_KWARGS = {
    "runtime": _lambda.Runtime.PYTHON_3_12,
    "architecture": _lambda.Architecture.X86_64,
    "tracing": _lambda.Tracing.ACTIVE,
    "timeout": cdk.Duration.minutes(1),
    "memory_size": 512,
}
LOG_LEVEL = "INFO"

LAMBDA_PARAMS = {
    "create-schema": Params(
        http_method="POST",
        http_path="create-schema",
        function_name="CreateSchema",
        function_path="create_schema",
        service="Schema",
        namespace="ServerlessDocumentAI",
    ),
    "delete-schema": Params(
        http_method="PUT",
        http_path="delete-schema",
        function_name="DeleteSchema",
        function_path="delete_schema",
        service="Schema",
        namespace="ServerlessDocumentAI",
    ),
    "get-schema": Params(
        http_method="POST",
        http_path="get-schema",
        function_name="GetSchema",
        function_path="get_schema",
        service="Schema",
        namespace="ServerlessDocumentAI",
    ),
    "list-schema": Params(
        http_method="POST",
        http_path="list-schema",
        function_name="ListSchema",
        function_path="list_schema",
        service="Schema",
        namespace="ServerlessDocumentAI",
    ),
    "extract-data": Params(
        http_method="POST",
        http_path="extract-data",
        function_name="ExtractData",
        function_path="extract_data",
        service="Extract",
        namespace="ServerlessDocumentAI",
    ),
    "extract-data-batch": Params(
        http_method="POST",
        http_path="extract-data-batch",
        function_name="ExtractDataBatch",
        function_path="extract_data_batch",
        service="Extract",
        namespace="ServerlessDocumentAI",
    ),
}
