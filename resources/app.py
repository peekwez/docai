#!/usr/bin/env python3
# import os
import aws_cdk as cdk

from resources.stacks.stack import DocumentAIStack

app = cdk.App()
DocumentAIStack(app, "DocumentAIStacksDev")
# DocumentAIStacks(app, "DocumentAIStacksProd")

app.synth()
