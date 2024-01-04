import json

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import llm, middleware, stream, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()


config = utils.Config()
resource = utils.Resource()

s3_client = resource.get_s3()
bucket_name = config.get_parameter("/env/bucket/name")
schema_table = resource.get_table("/env/schema/table/name")
extract_table = resource.get_table("/env/extract/table/name")
monitor_table = resource.get_table("/env/monitor/table/name")
openai_client = llm.LLMClient(
    json.loads(config.get_secret("/env/openai/secret/name"))["OPENAI_API_KEY"]
)


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)
    content: str = Field(..., min_length=1, max_length=10000000)
    mime_type: str = Field(..., min_length=1, max_length=64)


params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to extract data received",
        "SUCCESS": "Data extracted successfully",
        "ERROR": "Failed to extract data",
    },
    "include_fields": {"schema_name", "schema_version"},
    "annotation_key": "ExtractData",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def extract_data(request_id: str, req: dict):
    document = dict(content=req["content"], mime_type=req["mime_type"])
    key = dict(schema_name=req["schema_name"], schema_version=req["schema_version"])
    schema = schema_table.get_item(Key=key).get("Item")

    if not schema:
        raise exc.SchemaDoesNotExist

    try:
        params = stream.prepare_extraction_request(
            schema, document, s3_client, bucket_name
        )
        data = openai_client(**params, s3=s3_client, bucket_name=bucket_name)
    except Exception as e:
        error = dict(error_name=e.__class__.__name__, error_message=str(e))
        extract_table.put_item(Item=dict(request_id=request_id, **key, error=error))
        monitor_table.put_item(Item=dict(request_id=request_id, status="FAILED"))
        raise e

    extract_table.put_item(Item=dict(request_id=request_id, **key, **data))
    monitor_table.put_item(Item=dict(request_id=request_id, status="COMPLETED"))
    logger.info("Data extracted successfully", extra={"data": data})
    return {"request_id": request_id, "data": data["result"]}


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return extract_data(event["requestContext"]["requestId"], event["valid_body"])
