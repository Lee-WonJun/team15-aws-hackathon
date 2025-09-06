#!/usr/bin/env python3
import aws_cdk as cdk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from aws_config.config import AWS_ACCOUNT_ID, AWS_REGION
from mcp_stack import EntryMcpStack

app = cdk.App()

EntryMcpStack(
    app, 
    "EntryMcpStack",
    env=cdk.Environment(
        account=AWS_ACCOUNT_ID,
        region=AWS_REGION
    )
)

app.synth()