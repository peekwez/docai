import json

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

from docai import error, llm, utils

logger = Logger()
tracer = Tracer()
metrics = Metrics()

config = utils.Config()
bucket_name = config("FILES_BUCKET_PARAMETER_NAME")

resources = utils.Resources()
s3_client = resources.get_s3()
result_table = resources.get_table("RESULT_TABLE_PARAMETER_NAME")
monitor_table = resources.get_table("MONITOR_TABLE_PARAMETER_NAME")

secrets = utils.Secrets()
openai_client = llm.LLMClient(secrets("OPENAI_API_KEY_PARAMETER_NAME"))

RECEIVED = "Request to extract data in batch mode received"
SUCCESS = "Batch mode extraction completed successfully"
ERROR = "Failed to extract data in batch mode"
ANNOTATION_KEY = "ExtractDataBatchRun"


@tracer.capture_method
def extract_data(request_id: str, key: dict, payload: dict, **kwargs: dict):
    try:
        logger.info(RECEIVED, key)
        state = dict(request_id=request_id, status="RUNNING", created_at=utils.utcnow())
        monitor_table.put_item(Item=state)

        data = openai_client(**payload, s3=s3_client, bucket_name=bucket_name)

        result_table.put_item(Item=dict(request_id=request_id, **key, **data))
        state = dict(
            request_id=request_id, status="COMPLETED", created_at=utils.utcnow()
        )
        monitor_table.put_item(Item=state)

        logger.info(SUCCESS, extra={"data": data})
        tracer.put_annotation(ANNOTATION_KEY, "SUCCESS")
        tracer.put_metadata(ANNOTATION_KEY, data)
        metrics.add_metric(f"{ANNOTATION_KEY}Success", unit=MetricUnit.Count, value=1)
    except Exception as e:
        err = error.process_error(e)
        result_table.put_item(
            Item=dict(request_id=request_id, **key, error=err.log_dict())
        )
        state = dict(request_id=request_id, status="FAILED", created_at=utils.utcnow())
        monitor_table.put_item(Item=state)

        logger.error(ERROR, error=err.log_dict())
        tracer.put_annotation(ANNOTATION_KEY, "FAILED")
        metrics.add_metric(f"{ANNOTATION_KEY}Failed", unit=MetricUnit.Count, value=1)
        logger.exception(e)
        raise e


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event, context):
    for record in event["Records"]:
        req = json.loads((record["body"]))
        extract_data(**req)
