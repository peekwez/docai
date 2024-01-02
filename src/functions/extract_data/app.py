from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import llm, middleware, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()


resource = utils.Resource()
openai_client = llm.OpenAIClient()
schema_table = resource.get_table("/env/schema/table/name")
extract_table = resource.get_table("/env/extract/table/name")


class SchemaModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)


class DocumentModel(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000000)
    mime_type: str = Field(..., min_length=1, max_length=64)


class RequestModel(BaseModel):
    _schema: SchemaModel = Field(alias="schema")
    document: DocumentModel


params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to extract data received",
        "SUCCESS": "Data extracted successfully",
        "ERROR": "Failed to extract data",
    },
    "include_fields": {
        "schema_name",
        "schema_version",
    },
    "annotation_key": "ExtractData",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def extract_data(req: dict):
    document = req["document"]
    schema = schema_table.get_item(Key=req["schema"]).get("Item")

    if not schema:
        raise exc.SchemaDoesNotExist

    return openai_client(document, schema)


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return extract_data(event["valid_body"])
