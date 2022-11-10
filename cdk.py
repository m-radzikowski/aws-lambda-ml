#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.ml_stack import MLStack

app = cdk.App()
MLStack(app, "MLStack")

app.synth()
