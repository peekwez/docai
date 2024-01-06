from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, stream, utils


class RequestModel(BaseModel):
    schema_name: str = Field(..., min_length=4, max_length=64)
    schema_version: str = Field(..., length=10)
    content: str = Field(..., min_length=1, max_length=10000000)
    mime_type: str = Field(..., min_length=1, max_length=64)


class PayloadModel(BaseModel):
    schema_definition: dict
    text_data: str
    image_list: list[str] | None = None


class KeyModel(BaseModel):
    schema_name: str
    schema_version: str


class EventModel(BaseModel):
    request_id: str
    key: KeyModel
    payload: PayloadModel
    created_at: str = Field(default_factory=utils.utcnow)


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
batch_queue = resources.get_queue("BATCH_DATA_QUEUE_PARAMETER_NAME")


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
        payload = stream.prepare_extraction_request(
            schema, document, s3_client, bucket_name
        )
        event = EventModel(request_id=request_id, key=key, payload=payload)
        state = dict(request_id=request_id, status="QUEUED", created_at=utils.utcnow())
        batch_queue.send_message(MessageBody=event.json())
        monitor_table.put_item(Item=state)
    except Exception as e:
        error = dict(error_name=e.__class__.__name__, error_message=str(e))
        result_table.put_item(Item=dict(request_id=request_id, **key, error=error))
        state = dict(request_id=request_id, status="FAILED", created_at=utils.utcnow())
        monitor_table.put_item(Item=state)
        raise e

    return state


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return queue_batch_extraction(
        event["requestContext"]["requestId"], event["valid_body"]
    )
