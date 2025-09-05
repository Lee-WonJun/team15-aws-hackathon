#!/usr/bin/env python3
import aws_cdk as cdk
import os
from dotenv import load_dotenv
from bedrock_stack import BedrockStack

load_dotenv()

app = cdk.App()
BedrockStack(app, "BedrockStack-v2",
    env=cdk.Environment(
        account=os.getenv("AWS_ACCOUNT_ID"),
        region=os.getenv("AWS_REGION", "us-east-1")
    )
)

app.synth()