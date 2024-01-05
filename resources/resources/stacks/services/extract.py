import aws_cdk as cdk
from constructs import Construct

from resources.stacks.buckets import BucketsStack
from resources.stacks.queues import QueuesStack
from resources.stacks.secrets import SecretsStack
from resources.stacks.services.base import FunctionWithRoleAndDLQ
from resources.stacks.services.common import APIStack, LayersStack
from resources.stacks.tables import TablesStack

SERVICE = "Extract"
NAMESPACE = "ServerlessDocumentAI"


class ExtractServiceStack(cdk.NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        tables_stack: TablesStack,
        buckets_stack: BucketsStack,
        queues_stack: QueuesStack,
        secrets_stack: SecretsStack,
        layers_stack: LayersStack,
        api_stack: APIStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.__add_extract_data(
            tables_stack=tables_stack,
            buckets_stack=buckets_stack,
            secrets_stack=secrets_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )

        self.__add_extract_data_batch(
            tables_stack=tables_stack,
            buckets_stack=buckets_stack,
            secrets_stack=secrets_stack,
            queues_stack=queues_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )

    def __add_extract_data(
        self,
        tables_stack: TablesStack,
        buckets_stack: BucketsStack,
        secrets_stack: SecretsStack,
        layers_stack: LayersStack,
        api_stack: APIStack,
    ):
        self.extract_data = FunctionWithRoleAndDLQ(
            self,
            "ExtractData",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/extract_data",
        )
        tables_stack.add_access_to_schema_table(
            self.extract_data.fn,
            self.extract_data.role,
            ["dynamodb:GetItem"],
        )
        tables_stack.add_access_to_result_table(
            self.extract_data.fn,
            self.extract_data.role,
            ["dynamodb:PutItem"],
        )
        tables_stack.add_access_to_monitor_table(
            self.extract_data.fn,
            self.extract_data.role,
            ["dynamodb:PutItem"],
        )
        buckets_stack.add_access_to_files_bucket(
            self.extract_data.fn,
            self.extract_data.role,
            ["s3:*Object", "s3:ListBucket"],
        )
        secrets_stack.add_access_to_openai_secret(
            self.extract_data.fn,
            self.extract_data.role,
            ["secretsmanager:GetSecretValue"],
        )
        layers_stack.add_docai_layer(self.extract_data.fn)
        api_stack.add_endpoint(self.extract_data.fn, "POST", "extract-data")

    def __add_extract_data_batch(
        self,
        tables_stack: TablesStack,
        buckets_stack: BucketsStack,
        secrets_stack: SecretsStack,
        queues_stack: QueuesStack,
        layers_stack: LayersStack,
        api_stack: APIStack,
    ):
        self.extract_data_batch = FunctionWithRoleAndDLQ(
            self,
            "ExtractDataBatch",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/extract_data_batch",
        )
        tables_stack.add_access_to_schema_table(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["dynamodb:GetItem"],
        )
        tables_stack.add_access_to_result_table(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["dynamodb:PutItem"],
        )
        tables_stack.add_access_to_monitor_table(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["dynamodb:PutItem"],
        )
        buckets_stack.add_access_to_files_bucket(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["s3:*Object", "s3:ListBucket"],
        )
        queues_stack.add_access_to_batch_data_queue(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["sqs:SendMessage", "sqs:GetQueueUrl"],
        )
        secrets_stack.add_access_to_openai_secret(
            self.extract_data_batch.fn,
            self.extract_data_batch.role,
            ["secretsmanager:GetSecretValue"],
        )
        layers_stack.add_docai_layer(self.extract_data_batch.fn)
        api_stack.add_endpoint(self.extract_data_batch.fn, "POST", "extract-data-batch")
