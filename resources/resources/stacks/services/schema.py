import aws_cdk as cdk
from constructs import Construct

from resources.stacks.services.base import FunctionWithRoleAndDLQ
from resources.stacks.services.common import APIStack, LayersStack
from resources.stacks.tables import TablesStack

SERVICE = "Schema"
NAMESPACE = "ServerlessDocumentAI"


class SchemaServiceStack(cdk.NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        tables_stack: TablesStack,
        layers_stack: LayersStack,
        api_stack: APIStack,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.__add_create_schema(
            tables_stack=tables_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )
        self.__add_delete_schema(
            tables_stack=tables_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )
        self.__add_get_schema(
            tables_stack=tables_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )
        self.__add_list_schema(
            tables_stack=tables_stack,
            layers_stack=layers_stack,
            api_stack=api_stack,
        )

    def __add_create_schema(
        self, tables_stack: TablesStack, layers_stack: LayersStack, api_stack: APIStack
    ):
        self.create_schema = FunctionWithRoleAndDLQ(
            self,
            "CreateSchema",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/create_schema",
        )
        tables_stack.add_access_to_schema_table(
            self.create_schema.fn,
            self.create_schema.role,
            ["dynamodb:PutItem"],
        )
        layers_stack.add_docai_layer(self.create_schema.fn)
        api_stack.add_endpoint(self.create_schema.fn, "POST", "create-schema")

    def __add_delete_schema(
        self, tables_stack: TablesStack, layers_stack: LayersStack, api_stack: APIStack
    ):
        self.delete_schema = FunctionWithRoleAndDLQ(
            self,
            "DeleteSchema",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/delete_schema",
        )
        tables_stack.add_access_to_schema_table(
            self.delete_schema.fn,
            self.delete_schema.role,
            ["dynamodb:GetItem", "dynamodb:UpdateItem"],
        )
        layers_stack.add_docai_layer(self.delete_schema.fn)
        api_stack.add_endpoint(self.delete_schema.fn, "PUT", "delete-schema")

    def __add_get_schema(
        self, tables_stack: TablesStack, layers_stack: LayersStack, api_stack: APIStack
    ):
        self.get_schema = FunctionWithRoleAndDLQ(
            self,
            "GetSchema",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/get_schema",
        )
        tables_stack.add_access_to_schema_table(
            self.get_schema.fn,
            self.get_schema.role,
            ["dynamodb:GetItem"],
        )
        layers_stack.add_docai_layer(self.get_schema.fn)
        api_stack.add_endpoint(self.get_schema.fn, "POST", "get-schema")

    def __add_list_schema(
        self, tables_stack: TablesStack, layers_stack: LayersStack, api_stack: APIStack
    ):
        self.list_schema = FunctionWithRoleAndDLQ(
            self,
            "ListSchema",
            service=SERVICE,
            namespace=NAMESPACE,
            asset_suffix="functions/list_schema",
        )
        tables_stack.add_access_to_schema_table(
            self.list_schema.fn,
            self.list_schema.role,
            ["dynamodb:Query"],
        )
        layers_stack.add_docai_layer(self.list_schema.fn)
        api_stack.add_endpoint(self.list_schema.fn, "POST", "list-schema")
