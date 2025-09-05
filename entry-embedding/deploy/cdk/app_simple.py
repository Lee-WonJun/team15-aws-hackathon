#!/usr/bin/env python3
import aws_cdk as cdk
import os
from dotenv import load_dotenv
from simple_complete_stack import SimpleCompleteStack

load_dotenv()

app = cdk.App()
SimpleCompleteStack(app, "SimpleCompleteStack",
    env=cdk.Environment(
        account=os.getenv("AWS_ACCOUNT_ID"),
        region=os.getenv("AWS_REGION", "us-east-1")
    )
)

app.synth()