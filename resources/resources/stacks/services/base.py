from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class FunctionWithRoleAndDLQ(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        service: str,
        namespace: str,
        asset_suffix: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id)
        self.stage = self.node.try_get_context("stage")
        self.log_level = self.node.try_get_context("log_level")
        self.asset_root = Path(self.node.try_get_context("asset_root"))

        self.role = iam.Role(
            self,
            "Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        self.dlq = sqs.Queue(
            self,
            "DLQ",
            visibility_timeout=cdk.Duration.seconds(300),
            retention_period=cdk.Duration.days(14),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.fn = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            architecture=_lambda.Architecture.X86_64,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset(str(self.asset_root / asset_suffix)),
            dead_letter_queue=self.dlq,
            dead_letter_queue_enabled=True,
            role=self.role,
            environment={
                "DEAD_LETTER_QUEUE_NAME": self.dlq.queue_name,
                "POWERTOOLS_SERVICE_NAME": service,
                "POWERTOOLS_METRICS_NAMESPACE": namespace,
                "LOG_LEVEL": self.log_level,
            },
            timeout=cdk.Duration.seconds(300),
            memory_size=512,
            tracing=_lambda.Tracing.ACTIVE,
            log_retention=aws_logs.RetentionDays.ONE_YEAR,
        )
