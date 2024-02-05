from typing import Any, Callable

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext

from docai import error
from docai import exceptions as exc
from docai import models


def _validate_request(event: dict[str, Any], model: Any) -> Any:
    data = model.parse_raw(event["body"])
    return data


@lambda_handler_decorator(trace_execution=True)
def process_docai(
    handler: Callable[[dict[str, Any], LambdaContext], Any],
    event: dict[str, Any],
    context: LambdaContext,
    validation_model: Any,
    messages: dict[str, str],
    include_fields: list[str],
    annotation_key: str = "Schema",
    logger: Logger | None = None,
    tracer: Tracer | None = None,
    metrics: Metrics | None = None,
) -> Any:
    if logger is None:
        logger = Logger()

    if tracer is None:
        tracer = Tracer(auto_patch=False)

    if metrics is None:
        metrics = Metrics()

    handler = logger.inject_lambda_context(
        handler, correlation_id_path=correlation_paths.API_GATEWAY_REST
    )

    try:
        req = _validate_request(event, validation_model)
        logger.info(messages["RECEIVED"], req.dict(include=include_fields))

        event["valid_body"] = req.dict()
        data = handler(event, context)

        ret = models.ResultResponseModel(result=data)

        logger.info(messages["SUCCESS"], result=data)
        tracer.put_annotation(annotation_key, "SUCCESS")
        tracer.put_metadata(annotation_key, data)
        metrics.add_metric(f"{annotation_key}Success", unit=MetricUnit.Count, value=1)

    except exc.EXCEPTIONS as e:
        err = error.process_error(e)
        logger.error(messages["ERROR"], error=err.log_dict())
        tracer.put_annotation(annotation_key, "FAILED")
        metrics.add_metric(f"{annotation_key}Failed", unit=MetricUnit.Count, value=1)
        return {"statusCode": 400, "body": err.json()}

    except Exception as e:
        err = error.process_error(e)
        logger.error(messages["ERROR"], error=err.log_dict())
        tracer.put_annotation(annotation_key, "FAILED")
        metrics.add_metric(f"{annotation_key}Failed", unit=MetricUnit.Count, value=1)
        logger.exception(e)
        return {"statusCode": 500, "body": err.json()}

    return {"body": ret.json()}
