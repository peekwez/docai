import os
import boto3

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import BaseModel, Field
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

from docai_schema import middleware
from docai_schema import models
