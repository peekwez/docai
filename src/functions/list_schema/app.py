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


class ListSchemaRequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)


class ListSchemaResponseModel(BaseModel):
    count: int
    items: list[models.SchemaModel]


RECEIVED_MESSAGE = "Request to list schema `{0.schema_name}` versions received"
SUCCESS_MESSAGE = "Schema `{0.schema_name}` versions fetched"
ERROR_MESSAGE = "Failed to fetch schema {0.schema_name} versions - {1}"


@app.post("/list-schema")
@tracer.capture_method
def list_schema():
    try:
        req = ListSchemaRequestModel(**app.current_event.json_body)
        logger.info(RECEIVED_MESSAGE.format(req))

        data = table.query(
            KeyConditionExpression="schema_name = :schema_name",
            FilterExpression="schema_status <> :schema_status",
            ExpressionAttributeValues={
                ":schema_name": req.schema_name,
                ":schema_status": models.SchemaStatus.DELETED.value,
            },
        )
        if not data:
            raise exc.SchemaDoesNotExist

        items = [models.SchemaModel(**item) for item in data["Items"]]
        logger.info(SUCCESS_MESSAGE.format(req))

    except Exception as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        logger.exception(e)
        return error.process_error(e)

    tracer.put_metadata(req.schema_name, req.json())
    metrics.add_metric(name="ListSchema", unit=MetricUnit.Count, value=1)
    logger.info(items)
    ret = ListSchemaResponseModel(count=len(items), items=items)
    return ret.json()


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(logger=logger, tracer=tracer, annotation_key="Schema")
def lambda_handler(event, context):
    return app.resolve(event, context)
