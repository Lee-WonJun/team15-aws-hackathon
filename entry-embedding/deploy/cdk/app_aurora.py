#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from aurora_stack import AuroraRagStack

app = cdk.App()
AuroraRagStack(app, "AuroraRagStack",
    env=cdk.Environment(account="339712825274", region="us-east-1")
)
app.synth()
