#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from simple_rds_stack import SimpleRdsStack

app = cdk.App()
SimpleRdsStack(app, "SimpleRdsStack",
    env=cdk.Environment(account="339712825274", region="us-east-1")
)
app.synth()
