from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, models, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

resource = utils.Resource()
table = resource.get_table("/env/schema/table/name")


class GetSchemaRequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)


class GetSchemaResponseModel(models.SchemaModel):
    pass


class ErrorResponseModel(BaseModel):
    OK: bool = Field(default=False)
    error: str
    message: str


RECEIVED_MESSAGE = (
    "Request to fetch schema `{0.schema_name} - {0.schema_version}` received"
)
SUCCESS_MESSAGE = "Schema `{0.schema_name} - {0.schema_version}` fetched"
ERROR_MESSAGE = "Failed to fetch schema {0.schema_name} - {0.schema_version} - {1}"


@app.post("/get-schema")
@tracer.capture_method
def get_schema():
    req = GetSchemaRequestModel(**app.current_event.json_body)
    logger.info(RECEIVED_MESSAGE.format(req))
    try:
        key = {"schema_name": req.schema_name, "schema_version": req.schema_version}
        data = table.get_item(Key=key).get("Item")
        if not data:
            raise exc.SchemaDoesNotExist("Schema not found")

        if data["schema_status"] == models.SchemaStatus.DELETED.value:
            raise exc.SchemaDoesNotExist("Schema not found")

        schema = models.SchemaModel(**data)
        logger.info(SUCCESS_MESSAGE.format(req))

    except exc.SchemaDoesNotExist as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        return ErrorResponseModel(error="SchemaDoesNotExist", message=str(e)).json()

    except Exception as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        logger.exception(e)
        raise e

    tracer.put_metadata(req.schema_name, schema.json())
    metrics.add_metric(name="GetSchema", unit=MetricUnit.Count, value=1)

    ret = GetSchemaResponseModel(**data)
    return ret.json()


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(logger=logger, tracer=tracer, annotation_key="Schema")
def lambda_handler(event, context):
    return app.resolve(event, context)
