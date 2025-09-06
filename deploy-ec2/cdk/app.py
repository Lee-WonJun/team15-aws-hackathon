#!/usr/bin/env python3
import aws_cdk as cdk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from aws_config.config import AWS_ACCOUNT_ID, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from streamlit_stack_final import StreamlitChatbotStack

app = cdk.App()

StreamlitChatbotStack(
    app, 
    "StreamlitChatbotStack",
    env=cdk.Environment(
        account=AWS_ACCOUNT_ID,
        region=AWS_REGION
    )
)

app.synth()