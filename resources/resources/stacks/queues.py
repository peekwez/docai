import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class QueuesStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stage = self.node.try_get_context("stage")

        # Queue for processing batch requests
        self.batch_data = sqs.Queue(
            self,
            "ExtractDataBatchQueue",
            visibility_timeout=cdk.Duration.seconds(300),
            retention_period=cdk.Duration.days(14),
        )

        self.batch_data_param = ssm.StringParameter(
            self,
            "ExtractDataBatchQueueName",
            parameter_name=f"/{self.stage}/queue/batch_data_queue_name",
            string_value=self.batch_data.queue_name,
        )

        self.batch_data_arn = self.batch_data.queue_arn
        self.batch_data_param_arn = self.batch_data_param.parameter_arn
        self.batch_data_param_name = self.batch_data_param.parameter_name

    def add_access_to_batch_data_queue(
        self, fn: _lambda.Function, role: iam.Role, actions=list[str]
    ):
        fn.add_environment(
            "BATCH_DATA_QUEUE_PARAMETER_NAME", self.batch_data_param.parameter_name
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=actions,
                resources=[self.batch_data.queue_arn],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.batch_data_param.parameter_arn],
            )
        )

    def add_batch_data_as_event_source(self, fn: _lambda.Function):
        fn.add_event_source(
            lambda_event_sources.SqsEventSource(
                self.batch_data,
                batch_size=10,
            )
        )
