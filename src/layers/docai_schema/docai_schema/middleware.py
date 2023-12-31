import json
from typing import Callable

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from docai_schema import models


def _build_process_schema_context(event: dict) -> models.SchemaType:
    data = json.loads(event["body"])
    return dict(
        schema_name=data["schema_name"],
        schema_version=data.get("schema_version"),
    )


def _logger_inject_process_schema(logger: Logger, schema_context: dict):
    logger.structure_logs(append=True, **schema_context)


def _tracer_annotate_process_schema(tracer: Tracer, schema_context: dict):
    tracer.put_annotation(key="Schema", value=schema_context["schema_name"])


@lambda_handler_decorator(trace_execution=True)
def process_schema(
    handler: Callable,
    event: dict,
    context: LambdaContext,
    logger: Logger = None,
    tracer: Tracer = None,
) -> Callable:
    if logger is None:
        logger = Logger()

    if tracer is None:  # pragma: no cover
        tracer = Tracer(auto_patch=False)

    schema_context = _build_process_schema_context(event)
    handler = logger.inject_lambda_context(
        handler, correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True
    )

    _logger_inject_process_schema(logger=logger, schema_context=schema_context)
    _tracer_annotate_process_schema(tracer=tracer, schema_context=schema_context)
    return handler(event, context)
