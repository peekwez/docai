import os
from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from resources import constants as c


def create_role(scope: Construct, function_name: str) -> iam.Role:
    # extract_policies = []
    # if function_name.lower().find("batch") > -1:
    #     extract_policies = [
    #         iam.ManagedPolicy.from_aws_managed_policy_name(
    #             "service-role/AWSLambdaSQSQueueExecutionRole"
    #         )
    #     ]

    role = iam.Role(
        scope,
        f"DocumentAI{function_name}Role",
        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
        ],
    )
    return role


def create_tables(scope: Construct) -> dict[str, dynamodb.Table]:
    schema_table = dynamodb.Table(
        scope,
        "SchemaTable",
        partition_key=dynamodb.Attribute(
            name="schema_name", type=dynamodb.AttributeType.STRING
        ),
        sort_key=dynamodb.Attribute(
            name="schema_version", type=dynamodb.AttributeType.STRING
        ),
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )

    extract_table = dynamodb.Table(
        scope,
        "ExtractTable",
        partition_key=dynamodb.Attribute(
            name="request_id", type=dynamodb.AttributeType.STRING
        ),
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )

    monitor_table = dynamodb.Table(
        scope,
        "MonitorTable",
        partition_key=dynamodb.Attribute(
            name="request_id", type=dynamodb.AttributeType.STRING
        ),
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )

    return {
        "schema_table": schema_table,
        "extract_table": extract_table,
        "monitor_table": monitor_table,
    }


def create_bucket(scope: Construct) -> s3.Bucket:
    return s3.Bucket(
        scope,
        "DocumentAIBucket",
        removal_policy=cdk.RemovalPolicy.DESTROY,
        auto_delete_objects=True,
    )


def create_batch_queue(scope: Construct) -> sqs.Queue:
    return sqs.Queue(
        scope,
        "ExtractDataBatchQueue",
        visibility_timeout=cdk.Duration.seconds(300),
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )


def create_parameters(
    scope: Construct,
    schema_table: dynamodb.Table,
    extract_table: dynamodb.Table,
    monitor_table: dynamodb.Table,
    openai_credentials: secretsmanager.Secret,
    batch_queue: sqs.Queue,
    file_bucket: s3.Bucket,
) -> dict[str, ssm.StringParameter]:
    schema_param = ssm.StringParameter(
        scope,
        "SchemaTableName",
        parameter_name=f"/{c.STAGE}/env/schema/table/name",
        string_value=schema_table.table_name,
    )
    extract_param = ssm.StringParameter(
        scope,
        "ExtractTableName",
        parameter_name=f"/{c.STAGE}/env/extract/table/name",
        string_value=extract_table.table_name,
    )

    monitor_param = ssm.StringParameter(
        scope,
        "MonitorTableName",
        parameter_name=f"/{c.STAGE}/env/monitor/table/name",
        string_value=monitor_table.table_name,
    )

    openai_param = ssm.StringParameter(
        scope,
        "OpenAISecretsName",
        parameter_name=f"/{c.STAGE}/env/openai/secret/name",
        string_value=openai_credentials.secret_name,
    )

    queue_param = ssm.StringParameter(
        scope,
        "BatchQueueName",
        parameter_name=f"/{c.STAGE}/env/batch/queue/name",
        string_value=batch_queue.queue_name,
    )

    bucket_param = ssm.StringParameter(
        scope,
        "DocumentAIBucketName",
        parameter_name=f"/{c.STAGE}/env/bucket/name",
        string_value=file_bucket.bucket_name,
    )
    return {
        "schema_param": schema_param,
        "extract_param": extract_param,
        "monitor_param": monitor_param,
        "openai_param": openai_param,
        "batch_queue_param": queue_param,
        "file_bucket_param": bucket_param,
    }


def create_secrets(scope: Construct) -> secretsmanager.Secret:
    return secretsmanager.Secret(
        scope,
        "OpenAICredentials",
        secret_object_value={
            "OPENAI_API_KEY": cdk.SecretValue.unsafe_plain_text(
                os.environ["OPENAI_API_KEY"]
            ),
            "OPENAI_API_URL": cdk.SecretValue.unsafe_plain_text(
                os.environ["OPENAI_API_URL"]
            ),
        },
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )


def create_layers(scope: Construct) -> list[_lambda.LayerVersion]:
    layers = []
    bundle = cdk.BundlingOptions(
        image=_lambda.Runtime.PYTHON_3_12.bundling_image,
        command=["bash", "-c", c.BUNDLE_COMMAND],
    )
    for layer_path in c.LAYERS_ROOT.glob("*"):
        layer = _lambda.LayerVersion(
            scope,
            f"{layer_path.name}-layer",
            code=_lambda.Code.from_asset(f"{layer_path}", bundling=bundle),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            compatible_architectures=[_lambda.Architecture.X86_64],
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        layers.append(layer)
    return layers


def create_api(scope: Construct) -> tuple[apigw.RestApi, apigw.ApiKey]:
    api_key = apigw.ApiKey(
        scope,
        "DocumentAIGatewayKey",
        enabled=True,
    )

    api = apigw.RestApi(
        scope,
        "DocumentAIGateway",
        default_cors_preflight_options=apigw.CorsOptions(
            allow_origins=apigw.Cors.ALL_ORIGINS,
            allow_methods=apigw.Cors.ALL_METHODS,
        ),
        api_key_source_type=apigw.ApiKeySourceType.HEADER,
    )

    usage_plan = apigw.UsagePlan(
        scope,
        "DocumentAIGatewayUsagePlan",
        api_stages=[
            apigw.UsagePlanPerApiStage(
                api=api,
                stage=api.deployment_stage,
            )
        ],
    )
    usage_plan.add_api_key(api_key)

    return api, api_key


def create_lambda(
    scope: Construct,
    params: c.Params,
    api: apigw.RestApi,
    grants: Any,
    env: dict[str, str] = {},
    layers: list[_lambda.LayerVersion] = [],
) -> _lambda.Function:
    role = create_role(scope, params.function_name)

    dlq = sqs.Queue(
        scope,
        f"{params.function_name}DLQQueue",
        visibility_timeout=cdk.Duration.seconds(300),
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )
    env = {
        **env,
        "DEAD_LETTER_QUEUE_NAME": dlq.queue_name,
        "POWERTOOLS_SERVICE_NAME": params.service,
        "POWERTOOLS_METRICS_NAMESPACE": params.namespace,
        "LOG_LEVEL": c.LOG_LEVEL,
    }
    fn = _lambda.Function(
        scope,
        f"{params.function_name}Lambda",
        handler="app.lambda_handler",
        code=_lambda.Code.from_asset(f"{c.FUNCTIONS_ROOT / params.function_path}"),
        dead_letter_queue=dlq,
        dead_letter_queue_enabled=True,
        environment=env,
        layers=layers,
        role=role,
        log_retention=aws_logs.RetentionDays.SIX_MONTHS,
        **c.LAMBDA_KWARGS,
    )

    for resource, actions in grants:
        resource.grant(fn, *actions)

    fn_path = api.root.add_resource(params.http_path)
    fn_path.add_method(
        params.http_method, apigw.LambdaIntegration(fn), api_key_required=True
    )

    return fn
