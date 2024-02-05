import os

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SecretsStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stage = self.node.try_get_context("stage")
        self.openai = secretsmanager.Secret(
            self,
            "OpenaiAPIKeySecret",
            secret_string_value=cdk.SecretValue.unsafe_plain_text(
                os.environ["OPENAI_API_KEY"]
            ),
        )

        self.openai_param = ssm.StringParameter(
            self,
            "OpenaiAPIKeySecretName",
            parameter_name=f"/{self.stage}/secret/openai/api_key",
            string_value=self.openai.secret_name,
        )

        self.openai_arn = self.openai.secret_arn
        self.openai_param_arn = self.openai_param.parameter_arn
        self.openai_param_name = self.openai_param.parameter_name

    def add_access_to_openai_secret(
        self,
        fn: _lambda.Function,
        role: iam.Role,
        actions: list[str],
    ):
        fn.add_environment(
            "OPENAI_API_KEY_PARAMETER_NAME", self.openai_param.parameter_name
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=actions,
                resources=[self.openai.secret_arn],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.openai_param.parameter_arn],
            )
        )
