import json

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import llm, middleware, models, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

resource = utils.Resource()
config = utils.Config()
openai_client = llm.OpenAIClient()
schema_table = resource.get_table("/env/schema/table/name")
extract_table = resource.get_table("/env/extract/table/name")


class ExtractDataRequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)
    document: dict


class ExtractDataResponseModel(BaseModel):
    data: dict


class ErrorResponseModel(BaseModel):
    OK: bool = Field(default=False)
    error: str
    message: str


RECEIVED_MESSAGE = "Request to extract data using schema `{0.schema_name}` received"
SUCCESS_MESSAGE = (
    "Data extracted using `{0.schema_name}` with schema version `{0.schema_version}`"
)
ERROR_MESSAGE = "Failed to extract data using schema {0.schema_name} -  {1}"


@app.post("/extract-data")
@tracer.capture_method
def extract_data():
    req = ExtractDataRequestModel(**app.current_event.json_body)
    logger.info(RECEIVED_MESSAGE.format(req))
    try:
        document = models.DocumentModel(**req.document)

        key = {"schema_name": req.schema_name, "schema_version": req.schema_version}
        schema = schema_table.get_item(Key=key).get("Item")
        if not schema:
            raise exc.SchemaDoesNotExist("Schema not found")
        data = openai_client(document, schema)

        logger.info(SUCCESS_MESSAGE.format(schema))

    except (exc.InvalidData, exc.InvalidMimeType, exc.SchemaDoesNotExist) as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        return ErrorResponseModel(error=e.__class__.__name__, message=str(e)).json()

    except Exception as e:
        logger.error(ERROR_MESSAGE.format(req, e))
        logger.exception(e)
        raise e

    tracer.put_metadata(schema["schema_name"], schema.json())
    metrics.add_metric(name="ExtractData", unit=MetricUnit.Count, value=1)

    ret = ExtractDataResponseModel(data=data)
    return ret.json()


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(logger=logger, tracer=tracer, annotation_key="Extract")
def lambda_handler(event, context):
    return app.resolve(event, context)
