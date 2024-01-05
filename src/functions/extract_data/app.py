from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import llm, middleware, stream, utils


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)
    content: str = Field(..., min_length=1, max_length=10000000)
    mime_type: str = Field(..., min_length=1, max_length=64)


logger = Logger()
tracer = Tracer()
metrics = Metrics()

config = utils.Config()
bucket_name = config("FILES_BUCKET_PARAMETER_NAME")

resources = utils.Resources()
s3_client = resources.get_s3()
schema_table = resources.get_table("SCHEMA_TABLE_PARAMETER_NAME")
result_table = resources.get_table("RESULT_TABLE_PARAMETER_NAME")
monitor_table = resources.get_table("MONITOR_TABLE_PARAMETER_NAME")

secrets = utils.Secrets()
openai_client = llm.LLMClient(secrets("OPENAI_API_KEY_PARAMETER_NAME"))

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
        result_table.put_item(Item=dict(request_id=request_id, **key, error=error))
        monitor_table.put_item(
            Item=dict(request_id=request_id, status="FAILED", created_at=utils.utcnow())
        )
        raise e

    result_table.put_item(Item=dict(request_id=request_id, **key, **data))
    monitor_table.put_item(
        Item=dict(request_id=request_id, status="COMPLETED", created_at=utils.utcnow())
    )
    logger.info("Data extracted successfully", extra={"data": data})
    return {"request_id": request_id, "data": data["result"]}


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return extract_data(event["requestContext"]["requestId"], event["valid_body"])
