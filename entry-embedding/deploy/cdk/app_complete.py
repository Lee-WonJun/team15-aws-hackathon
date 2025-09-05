#!/usr/bin/env python3
import aws_cdk as cdk
import os
from dotenv import load_dotenv
from complete_stack import CompleteEntryRagStack

load_dotenv()

app = cdk.App()
CompleteEntryRagStack(app, "CompleteEntryRagStack",
    env=cdk.Environment(
        account=os.getenv("AWS_ACCOUNT_ID"),
        region=os.getenv("AWS_REGION", "us-west-2")
    )
)

app.synth()