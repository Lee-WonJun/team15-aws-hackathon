#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from step1_infrastructure import Step1InfrastructureStack

app = cdk.App()
Step1InfrastructureStack(app, "Step1Infrastructure",
    env=cdk.Environment(account=os.environ['AWS_ACCOUNT_ID'], region=os.environ['AWS_REGION'])
)
app.synth()
