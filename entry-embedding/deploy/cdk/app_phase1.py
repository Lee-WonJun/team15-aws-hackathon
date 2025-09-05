#!/usr/bin/env python3
import aws_cdk as cdk
from entry_rag_stack_phase1 import EntryRagStackPhase1
import os

app = cdk.App()

# 환경 변수에서 계정 정보 가져오기
account = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION', 'us-east-1')

EntryRagStackPhase1(app, "EntryRagStackPhase1",
    env=cdk.Environment(account=account, region=region)
)

app.synth()