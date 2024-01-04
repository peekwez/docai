import os

import aws_cdk as cdk
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_apigateway as apigw
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
        monitor_table = tables["monitor_table"]

        # S3 Bucket
        file_bucket = utils.create_bucket(self)

        # Batch Queue
        batch_queue = utils.create_batch_queue(self)

        # Layers
        layers = utils.create_layers(self)

        # Secrets
        openai_secret = utils.create_secrets(self)

        # Parameters
        parameters = utils.create_parameters(
            self,
            schema_table,
            extract_table,
            monitor_table,
            openai_secret,
            batch_queue,
            file_bucket,
        )
        schema_param = parameters["schema_param"]
        extract_param = parameters["extract_param"]
        openai_param = parameters["openai_param"]
        monitor_param = parameters["monitor_param"]
        batch_queue_param = parameters["batch_queue_param"]
        file_bucket_param = parameters["file_bucket_param"]

        # API Gateway
        api, api_key = utils.create_api(self)

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
                (monitor_table, ["dynamodb:PutItem"]),
            ],
            "extract-data-batch": [
                (schema_table, ["dynamodb:GetItem"]),
                (extract_table, ["dynamodb:PutItem"]),
                (monitor_table, ["dynamodb:PutItem"]),
                (batch_queue, ["sqs:SendMessage", "sqs:GetQueueUrl"]),
            ],
        }
        fns = []
        for key, params in c.LAMBDA_PARAMS.items():
            service = params.service
            fn = utils.create_lambda(self, params, api, grants[key], **kwargs)
            fns.append(fn)
            schema_param.grant_read(fn)

            if service == "Extract":
                file_bucket.grant_read_write(fn)
                file_bucket_param.grant_read(fn)
                extract_param.grant_read(fn)
                monitor_param.grant_read(fn)
                openai_param.grant_read(fn)
                openai_secret.grant_read(fn)
                batch_queue_param.grant_read(fn)

        # cdk.CfnOutput(
        #     self,
        #     "DocumentAIGatewayURL",
        #     value=api.url,
        # )

        # cdk.CfnOutput(
        #     self,
        #     "DocumentAIGatewayKey",
        #     value=api_key.key_id,
        # )
