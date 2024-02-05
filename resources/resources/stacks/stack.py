import aws_cdk as cdk
from constructs import Construct

from resources.stacks.buckets import BucketsStack
from resources.stacks.queues import QueuesStack
from resources.stacks.secrets import SecretsStack
from resources.stacks.services.common import APIStack, LayersStack
from resources.stacks.services.extract import ExtractServiceStack
from resources.stacks.services.schema import SchemaServiceStack
from resources.stacks.tables import TablesStack


class DocumentAIStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        # stateful resources
        self.tables = TablesStack(self, "TablesStack")
        self.buckets = BucketsStack(self, "BucketsStack")
        self.queues = QueuesStack(self, "QueuesStack")
        self.secrets = SecretsStack(self, "SecretsStack")

        # stateless resources
        self.api = APIStack(self, "APIStack")
        self.layers = LayersStack(self, "LayersStack")
        self.schema_service = SchemaServiceStack(
            self,
            "SchemaServiceStack",
            tables_stack=self.tables,
            layers_stack=self.layers,
            api_stack=self.api,
        )

        self.extract_service = ExtractServiceStack(
            self,
            "ExtractServiceStack",
            tables_stack=self.tables,
            buckets_stack=self.buckets,
            secrets_stack=self.secrets,
            queues_stack=self.queues,
            layers_stack=self.layers,
            api_stack=self.api,
        )
