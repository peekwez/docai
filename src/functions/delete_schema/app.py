from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, models, utils


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)


logger = Logger()
tracer = Tracer()
metrics = Metrics()

table = utils.Resource().get_table("/env/schema/table/name")
params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to fetch schema received",
        "SUCCESS": "Schema fetched",
        "ERROR": "Failed to fetch schema",
    },
    "include_fields": {"schema_name", "schema_version"},
    "annotation_key": "GetSchema",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


def delete_schema(req: dict):
    data = table.get_item(Key=req).get("Item")
    if not data:
        raise exc.SchemaDoesNotExist

    if data["schema_status"] == models.SchemaStatus.DELETED.value:
        raise exc.SchemaDoesNotExist

    table.update_item(
        Key=req,
        UpdateExpression="SET schema_status = :schema_status",
        ExpressionAttributeValues={":schema_status": models.SchemaStatus.DELETED.value},
    )
    return dict(message="Schema deleted successfully")


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return delete_schema(event["valid_body"])
