import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class TablesStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stage = self.node.try_get_context("stage")

        # Table for storing schemas
        self.schema = dynamodb.Table(
            self,
            "SchemaTable",
            partition_key=dynamodb.Attribute(
                name="schema_name", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="schema_version", type=dynamodb.AttributeType.STRING
            ),
        )
        self.schema_param = ssm.StringParameter(
            self,
            "SchemaTableName",
            parameter_name=f"/{self.stage}/table/schema_table_name",
            string_value=self.schema.table_name,
        )
        self.schema_arn = self.schema.table_arn
        self.schema_param_arn = self.schema_param.parameter_arn
        self.schema_param_name = self.schema_param.parameter_name

        # Table for storing request and extraction results
        self.result = dynamodb.Table(
            self,
            "ResultTable",
            partition_key=dynamodb.Attribute(
                name="request_id", type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_IMAGE,
        )
        self.result_param = ssm.StringParameter(
            self,
            "ResultTableName",
            parameter_name=f"/{self.stage}/table/result_table_name",
            string_value=self.result.table_name,
        )
        self.result_arn = self.result.table_arn
        self.result_param_arn = self.result_param.parameter_arn
        self.result_param_name = self.result_param.parameter_name

        # Table for monitoring the status of the extraction
        self.monitor = dynamodb.Table(
            self,
            "MonitorTable",
            partition_key=dynamodb.Attribute(
                name="request_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at", type=dynamodb.AttributeType.STRING
            ),
        )

        self.monitor_param = ssm.StringParameter(
            self,
            "MonitorTableName",
            parameter_name=f"/{self.stage}/table/monitor_table_name",
            string_value=self.monitor.table_name,
        )
        self.monitor_arn = self.monitor.table_arn
        self.monitor_param_arn = self.monitor_param.parameter_arn
        self.monitor_param_name = self.monitor_param.parameter_name

    def add_access_to_schema_table(
        self,
        fn: _lambda.Function,
        role: iam.Role,
        actions: list[str],
    ):
        fn.add_environment(
            "SCHEMA_TABLE_PARAMETER_NAME", self.schema_param.parameter_name
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=actions,
                resources=[self.schema.table_arn],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.schema_param.parameter_arn],
            )
        )

    def add_access_to_result_table(
        self,
        fn: _lambda.Function,
        role: iam.Role,
        actions: list[str],
    ):
        fn.add_environment(
            "RESULT_TABLE_PARAMETER_NAME", self.result_param.parameter_name
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=actions,
                resources=[self.result.table_arn],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.result_param.parameter_arn],
            )
        )

    def add_access_to_monitor_table(
        self,
        fn: _lambda.Function,
        role: iam.Role,
        actions: list[str],
    ):
        fn.add_environment(
            "MONITOR_TABLE_PARAMETER_NAME", self.monitor_param.parameter_name
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=actions,
                resources=[self.monitor.table_arn],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=[self.monitor_param.parameter_arn],
            )
        )
