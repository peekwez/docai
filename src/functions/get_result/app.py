from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from docai import exceptions as exc
from docai import middleware, stream, utils


class RequestModel(BaseModel):
    request_id: str


logger = Logger()
tracer = Tracer()
metrics = Metrics()

resources = utils.Resources()
result_table = resources.get_table("RESULT_TABLE_PARAMETER_NAME")
monitor_table = resources.get_table("MONITOR_TABLE_PARAMETER_NAME")


params = {
    "validation_model": RequestModel,
    "messages": {
        "RECEIVED": "Request to get result received",
        "SUCCESS": "Result has been retrieved successfully",
        "ERROR": "Failed to retrieve results for request",
    },
    "include_fields": {"request_id"},
    "annotation_key": "GetResult",
    "logger": logger,
    "tracer": tracer,
    "metrics": metrics,
}


@tracer.capture_method
def get_result(request_id: str):
    states = monitor_table.query(
        KeyConditionExpression="request_id = :request_id",
        ExpressionAttributeValues={
            ":request_id": request_id,
        },
        ScanIndexForward=False,  # Sort in descending order
    )

    if not states:
        raise exc.RequestDoesNotExist

    state = states["Items"][0]
    if state["status"] in ["COMPLETED", "FAILED"]:
        result = result_table.get_item(Key=dict(request_id=request_id)).get("Item")
        if state["status"] == "COMPLETED":
            state.update(status="COMPLETED", data=result["result"])
        elif state["status"] == "FAILED":
            state.update(status="FAILED", error=result["error"])
    return state


@metrics.log_metrics(capture_cold_start_metric=True)
@middleware.process_docai(**params)
def lambda_handler(event, context):
    return get_result(event["valid_body"]["request_id"])
