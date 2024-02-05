from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, models, utils


class RequestModel(BaseModel):
    schema_name: str | None = Field(default=None, min_length=4, max_length=64)
    page_number: int = Field(default=1, gt=0)
    page_size: int = Field(default=50, gt=0, le=100)


logger = Logger()
tracer = Tracer()
metrics = Metrics()

resources = utils.Resources()
schema_table = resources.get_table("SCHEMA_TABLE_PARAMETER_NAME")

params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to list schema versions received",
        "SUCCESS": "Schema versions fetched",
        "ERROR": "Failed to fetch schema versions",
    },
    "include_fields": {"schema_name"},
    "annotation_key": "ListSchema",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def list_schema(req: dict) -> dict:
    if not req["schema_name"]:
        data = schema_table.scan(
            FilterExpression="schema_status <> :schema_status",
            ExpressionAttributeValues={
                ":schema_status": models.SchemaStatus.DELETED.value,
            },
            Limit=req["page_size"],
        )
    else:
        data = schema_table.query(
            KeyConditionExpression="schema_name = :schema_name",
            FilterExpression="schema_status <> :schema_status",
            ExpressionAttributeValues={
                ":schema_name": req["schema_name"],
                ":schema_status": models.SchemaStatus.DELETED.value,
            },
        )

        if not data:
            raise exc.SchemaDoesNotExist

    items = [item for item in data["Items"]]
    return {"count": len(items), "items": items}


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context) -> dict:
    return list_schema(event["valid_body"])
