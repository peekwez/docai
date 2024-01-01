import os

from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from resources import constants as c
from resources import utils


class DocumentAIStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamoDB Tables
        tables = utils.create_tables(self)
        schema_table = tables["schema_table"]
        extract_table = tables["extract_table"]

        # Layers
        layers = utils.create_layers(self)

        # Secrets
        openai_secret = utils.create_secrets(self)

        # Parameters
        parameters = utils.create_parameters(
            self, schema_table, extract_table, openai_secret
        )
        schema_param = parameters["schema_param"]
        extract_param = parameters["extract_param"]
        openai_param = parameters["openai_param"]

        # API Gateway
        api = apigw.RestApi(self, "DocumentAIGateway")

        # Function Params
        kwargs = dict(layers=layers, env={"STAGE": c.STAGE})
        grants = {
            "create-schema": [(schema_table, ["dynamodb:PutItem"])],
            "get-schema": [(schema_table, ["dynamodb:GetItem"])],
            "list-schema": [(schema_table, ["dynamodb:Query"])],
            "delete-schema": [
                (schema_table, ["dynamodb:GetItem", "dynamodb:UpdateItem"])
            ],
            "extract-data": [
                (schema_table, ["dynamodb:GetItem"]),
                (extract_table, ["dynamodb:PutItem"]),
            ],
        }
        fns = []
        for key, params in c.LAMBDA_PARAMS.items():
            service = params.service
            fn = utils.create_lambda(self, params, api, grants[key], **kwargs)
            fns.append(fn)

            if service == "Schema":
                schema_param.grant_read(fn)
            elif service == "Extract":
                schema_param.grant_read(fn)
                extract_param.grant_read(fn)
                openai_param.grant_read(fn)
                openai_secret.grant_read(fn)
