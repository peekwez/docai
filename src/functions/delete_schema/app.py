from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import error
from docai import exceptions as exc
from docai import middleware, models, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

resource = utils.Resource()
table = resource.get_table("/env/schema/table/name")


class DeleteSchemaRequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)


class DeleteSchemaResponseModel(BaseModel):
    OK: bool = Field(default=True)
    message: str = Field(default="Schema deleted successfully")


RECEIVED_MESSAGE = (
    "Request to delete schema `{0.schema_name} - {0.schema_version}` received"
)
SUCCESS_MESSAGE = "Schema `{0.schema_name} - {0.schema_version}` deleted"
ERROR_MESSAGE = "Failed to update schema {0.schema_name} - {0.schema_version} - {1}"


@app.put("/delete-schema")
@tracer.capture_method
def delete_schema():
    try:
        req = DeleteSchemaRequestModel(**app.current_event.json_body)
        logger.info(RECEIVED_MESSAGE.format(req))

        key = {"schema_name": req.schema_name, "schema_version": req.schema_version}
        data = table.get_item(Key=key).get("Item")
        if not data:
            raise exc.SchemaDoesNotExist

        if data["schema_status"] == models.SchemaStatus.DELETED.value:
            raise exc.SchemaDoesNotExist

        schema = models.SchemaModel(**data)
        table.update_item(
            Key=key,
            UpdateExpression="SET schema_status = :schema_status",
            ExpressionAttributeValues={
                ":schema_status": models.SchemaStatus.DELETED.value
            },
        )
        logger.info(SUCCESS_MESSAGE.format(req))
    except Exception as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        logger.exception(e)
        return error.process_error(e)

    tracer.put_metadata(req.schema_name, schema.json())
    metrics.add_metric(name="DeleteSchema", unit=MetricUnit.Count, value=1)

    ret = DeleteSchemaResponseModel()
    return ret.json()


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(logger=logger, tracer=tracer, annotation_key="Schema")
def lambda_handler(event, context):
    return app.resolve(event, context)
