#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
)
from constructs import Construct

class McpLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function
        mcp_lambda = _lambda.Function(
            self, "McpLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("."),
            timeout=Duration.seconds(30),
            memory_size=512
        )

        # API Gateway
        api = apigateway.RestApi(
            self, "McpApi",
            rest_api_name="MCP Server API",
            description="MCP Server API Gateway"
        )

        # Lambda integration
        lambda_integration = apigateway.LambdaIntegration(mcp_lambda)
        
        # Add proxy resource
        api.root.add_proxy(
            default_integration=lambda_integration,
            any_method=True
        )

app = cdk.App()
McpLambdaStack(app, "McpLambdaStack")
app.synth()
