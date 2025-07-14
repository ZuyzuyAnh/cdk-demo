import aws_cdk as cdk
from aws_cdk.assertions import Template
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra')))

from todo import TodoStack

def test_stack_has_dynamodb_table():
    app = cdk.App()
    stack = TodoStack(app, "TodoStackTest")
    template = Template.from_stack(stack)

    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST"
    })

    template.resource_count_is("AWS::Lambda::Function", 1)
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)

def test_lambda_function_properties():
    app = cdk.App()
    stack = TodoStack(app, "TodoStackTest")
    template = Template.from_stack(stack)
    
    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": "python3.9",
        "Handler": "handler.main"
    })

def test_api_gateway_methods():
    app = cdk.App()
    stack = TodoStack(app, "TodoStackTest")
    template = Template.from_stack(stack)
    
    # Check that we have the expected API Gateway methods
    template.resource_count_is("AWS::ApiGateway::Method", 5)  # GET, POST, PUT, DELETE, and proxy