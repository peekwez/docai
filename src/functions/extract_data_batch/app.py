from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, stream, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()

config = utils.Config()
resource = utils.Resource()

bucket_name = config.get_parameter("/env/bucket/name")
schema_table = resource.get_table("/env/schema/table/name")
extract_table = resource.get_table("/env/extract/table/name")
monitor_table = resource.get_table("/env/monitor/table/name")
batch_queue = resource.get_queue("/env/batch/queue/name")
s3_client = resource.get_s3()


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)
    content: str = Field(..., min_length=1, max_length=10000000)
    mime_type: str = Field(..., min_length=1, max_length=64)


class PayloadModel(BaseModel):
    request_id: str
    schema_definition: dict
    text_data: str
    image_list: list[str] | None = None


params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to extract data in batch mode received",
        "SUCCESS": "Batch mode extraction task queued successfully",
        "ERROR": "Failed to queue batch mode extraction",
    },
    "include_fields": {"schema_name", "schema_version"},
    "annotation_key": "ExtractDataBatch",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def queue_batch_extraction(request_id: str, req: dict):
    document = dict(content=req["content"], mime_type=req["mime_type"])
    key = dict(schema_name=req["schema_name"], schema_version=req["schema_version"])
    schema = schema_table.get_item(Key=key).get("Item")

    if not schema:
        raise exc.SchemaDoesNotExist

    try:
        params = stream.prepare_extraction_request(
            schema, document, s3_client, bucket_name
        )
        payload = PayloadModel(request_id=request_id, **params)
        batch_queue.send_message(MessageBody=payload.json())
        monitor_table.put_item(Item=dict(request_id=request_id, status="QUEUED"))
    except Exception as e:
        error = dict(error_name=e.__class__.__name__, error_message=str(e))
        extract_table.put_item(Item=dict(request_id=request_id, **key, error=error))
        monitor_table.put_item(Item=dict(request_id=request_id, status="FAILED"))
        raise e
    return {"request_id": request_id, "status": "QUEUED", "data": None}


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return queue_batch_extraction(
        event["requestContext"]["requestId"], event["valid_body"]
    )
