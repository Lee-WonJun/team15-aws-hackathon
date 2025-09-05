#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from step2_bedrock import Step2BedrockStack

app = cdk.App()
Step2BedrockStack(app, "Step2Bedrock",
    collection_arn="arn:aws:aoss:us-east-1:339712825274:collection/2wxf05037t8sqmasymnj",
    bucket_arn="arn:aws:s3:::entry-python-docs-339712825274-us-east-1",
    env=cdk.Environment(account="339712825274", region="us-east-1")
)
app.synth()
