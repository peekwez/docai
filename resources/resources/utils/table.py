from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from resources import constants as c


class DocumentAITableStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Schema Table
        self.schema = dynamodb.Table(
            scope,
            "SchemaTable",
            partition_key=dynamodb.Attribute(
                name="schema_name", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="schema_version", type=dynamodb.AttributeType.STRING
            ),
        )
        self.schema_param = ssm.StringParameter(
            scope,
            "SchemaTableName",
            parameter_name=f"/{c.STAGE}/schema_table_name",
            string_value=self.schema.table_name,
        )

        # Extract Table
        self.extract = dynamodb.Table(
            scope,
            "ExtractTable",
            partition_key=dynamodb.Attribute(
                name="request_id", type=dynamodb.AttributeType.STRING
            ),
        )
        self.extract_param = ssm.StringParameter(
            scope,
            "ExtractTableName",
            parameter_name=f"/{c.STAGE}/extract_table_name",
            string_value=self.extract.table_name,
        )

        # Monitor Table
        self.monitor = dynamodb.Table(
            scope,
            "MonitorTable",
            partition_key=dynamodb.Attribute(
                name="request_id", type=dynamodb.AttributeType.STRING
            ),
        )

        self.monitor_param = ssm.StringParameter(
            scope,
            "MonitorTableName",
            parameter_name=f"/{c.STAGE}/monitor_table_name",
            string_value=self.monitor.table_name,
        )
