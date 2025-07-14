#!/usr/bin/env python3
import aws_cdk as cdk
from todo import TodoStack

app = cdk.App()
TodoStack(app, "TodoStack")
app.synth()