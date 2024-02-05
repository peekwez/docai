from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import middleware, models, utils


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_description: str = Field(..., min_length=8, max_length=1028)
    schema_definition: dict


logger = Logger()
tracer = Tracer()
metrics = Metrics()

resources = utils.Resources()
schema_table = resources.get_table("SCHEMA_TABLE_PARAMETER_NAME")

params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to create schema received",
        "SUCCESS": "Schema created successfully",
        "ERROR": "Failed to create schema",
    },
    "include_fields": {"schema_name", "schema_version"},
    "annotation_key": "CreateSchema",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def create_schema(req: dict):
    schema = models.SchemaModel(**req)
    schema_table.put_item(Item=schema.dict())
    return schema.dict(include={"schema_name", "schema_version", "number_of_tokens"})


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return create_schema(event["valid_body"])
