from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import error, middleware, models, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()


resource = utils.Resource()
table = resource.get_table("/env/schema/table/name")


class CreateSchemaRequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_description: str = Field(..., min_length=8, max_length=1028)
    schema_definition: dict


class CreateSchemaResponseModel(BaseModel):
    schema_name: str
    schema_version: str
    number_of_tokens: int


RECEIVED_MESSAGE = "Request to create schema `{0.schema_name}` received"
SUCCESS_MESSAGE = "Schema `{0}` created with schema version `{0.schema_version}`"
ERROR_MESSAGE = "Failed to create schema {0.schema_name} -  {1}"


@app.post("/create-schema")
@tracer.capture_method
def create_schema():
    try:
        req = CreateSchemaRequestModel(**app.current_event.json_body)
        logger.info(RECEIVED_MESSAGE.format(req))

        schema = models.SchemaModel(
            schema_name=req.schema_name,
            schema_description=req.schema_description,
            schema_definition=req.schema_definition,
        )
        table.put_item(Item=schema.dict())
        logger.info(SUCCESS_MESSAGE.format(schema))

    except Exception as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        logger.exception(e)
        return error.process_error(e)

    tracer.put_metadata(schema.schema_name, schema.json())
    metrics.add_metric(name="CreateSchema", unit=MetricUnit.Count, value=1)

    ret = CreateSchemaResponseModel(
        schema_name=schema.schema_name,
        schema_version=schema.schema_version,
        number_of_tokens=schema.number_of_tokens,
    )
    return ret.json()


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(logger=logger, tracer=tracer, annotation_key="Schema")
def lambda_handler(event, context):
    return app.resolve(event, context)
