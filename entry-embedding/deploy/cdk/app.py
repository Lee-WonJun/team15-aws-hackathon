#!/usr/bin/env python3
import aws_cdk as cdk
import os
from dotenv import load_dotenv
from entry_rag_stack import EntryRagStack

# .env 파일 로드
load_dotenv()

app = cdk.App()
EntryRagStack(app, "EntryRagStack",
    env=cdk.Environment(
        account=os.getenv("AWS_ACCOUNT_ID"),
        region=os.getenv("AWS_REGION", "us-west-2")
    )
)

app.synth()