import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct


class LambdaFunctionRole(Construct):
    def __init__(self, scope: Construct, id: str, function_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.role = iam.Role(
            self,
            f"{function_name}LambdaFunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:UpdateItem",
                ],
                resources=[
                    "arn:aws:dynamodb:us-east-1:123456789012:table/SchemaTable",
                    "arn:aws:dynamodb:us-east-1:123456789012:table/ExtractTable",
                    "arn:aws:dynamodb:us-east-1:123456789012:table/MonitorTable",
                ],
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "sqs:SendMessage",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                ],
                resources=[
                    "arn:aws:sqs:us-east-1:123456789012:DocumentAIQueue",
                ],
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket",
                ],
                resources=[
                    "arn:aws:s3:::document-ai-bucket",
                    "arn:aws:s3:::document-ai-bucket/*",
                ],
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "secretsmanager:GetSecretValue",
                ],
                resources=[
                    "arn:aws:secretsmanager:us-east-1:123456789012:secret:OpenAI-*",
                ],
            )
        )

        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ssm:GetParameter",
                ],
                resources=[
                    "arn:aws:ssm:us-east-1:123456789012:parameter/DocumentAI-*",
                ],
            )
        )
