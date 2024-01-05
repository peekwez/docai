import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class BucketsStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stage = self.node.try_get_context("stage")

        # Bucket for storing files to extract data from
        self.files = s3.Bucket(
            self,
            "FilesBucket",
        )

        self.files_param = ssm.StringParameter(
            self,
            "FilesBucketName",
            parameter_name=f"/{self.stage}/bucket/files_bucket_name",
            string_value=self.files.bucket_name,
        )

    def add_access_to_files_bucket(
        self, fn: _lambda.Function, role: iam.Role, actions=list[str]
    ):
        fn.add_environment(
            "FILES_BUCKET_PARAMETER_NAME", self.files_param.parameter_name
        )

        bucket_actions = list(filter(lambda x: x.endswith("Bucket"), actions))
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=bucket_actions,
                resources=[self.files.bucket_arn],
            )
        )

        object_actions = list(filter(lambda x: x.endswith("Object"), actions))
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=object_actions,
                resources=[f"{self.files.bucket_arn}/*"],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.files_param.parameter_arn],
            )
        )
