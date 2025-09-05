#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
)
from constructs import Construct

class McpStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function
        mcp_lambda = _lambda.Function(
            self, "McpFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("."),
            timeout=Duration.seconds(30)
        )

        # API Gateway
        api = apigateway.RestApi(
            self, "McpApi",
            rest_api_name="MCP Server"
        )

        # Lambda integration
        integration = apigateway.LambdaIntegration(mcp_lambda)
        api.root.add_proxy(default_integration=integration, any_method=True)

app = cdk.App()
McpStack(app, "McpStack")
app.synth()
