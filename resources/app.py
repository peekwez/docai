#!/usr/bin/env python3
# import os

import aws_cdk as cdk

from resources import constants as c
from resources.stack import DocumentAIStack

app = cdk.App()
DocumentAIStack(app, f"DocumentAIStack{c.STAGE.title()}")

app.synth()
