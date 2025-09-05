#!/usr/bin/env python3
import aws_cdk as cdk
import sys
sys.path.append('..')
from step1_infrastructure import Step1InfrastructureStack
import os

app = cdk.App()
Step1InfrastructureStack(app, "Step1Infrastructure",
    env=cdk.Environment(
        account=os.environ.get('AWS_ACCOUNT_ID'),
        region=os.environ.get('AWS_REGION', 'us-east-1')
    )
)
app.synth()
