#!/usr/bin/env python3
import os
import aws_cdk as cdk
from lyrr.lyrr_stack import LyrrStack

app = cdk.App()
LyrrStack(app, "LyrrStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
