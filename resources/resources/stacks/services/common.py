from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

BUNDLE_COMMAND = (
    "pip install -r requirements.txt -t "
    "/asset-output/python && "
    "cp -a {name} /asset-output/python"
)


class LayersStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.asset_root = Path(self.node.try_get_context("asset_root"))

        docai_path = self.asset_root / "layers" / "docai"
        docai_cmd = BUNDLE_COMMAND.format(name=docai_path.name)
        self.docai = _lambda.LayerVersion(
            self,
            "DocumentAILayer",
            code=_lambda.Code.from_asset(
                str(docai_path),
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=["bash", "-c", docai_cmd],
                ),
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            compatible_architectures=[_lambda.Architecture.X86_64],
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

    def add_docai_layer(self, fn: _lambda.Function) -> None:
        fn.add_layers(self.docai)


class APIStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.api = apigw.RestApi(
            self,
            "APIGateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
            api_key_source_type=apigw.ApiKeySourceType.HEADER,
        )
        self.create_api_key(quota=1000)

    def add_endpoint(
        self, fn: _lambda.Function, http_method: str, http_path: str
    ) -> None:
        fn_path = self.api.root.add_resource(http_path)
        fn_path.add_method(
            http_method, apigw.LambdaIntegration(fn), api_key_required=True
        )

    def create_api_key(self, quota: int = 10000) -> None:
        usage_plan = apigw.UsagePlan(
            self,
            f"UsagePlan{quota}PerMonth",
            api_stages=[
                apigw.UsagePlanPerApiStage(
                    api=self.api, stage=self.api.deployment_stage
                )
            ],
            quota=apigw.QuotaSettings(limit=10000, period=apigw.Period.MONTH),
            throttle=apigw.ThrottleSettings(rate_limit=10, burst_limit=2),
        )
        api_key = apigw.ApiKey(self, "ApiKey", enabled=True)
        usage_plan.add_api_key(api_key)
        cdk.CfnOutput(self, "ApiKeyId", value=api_key.key_id)
