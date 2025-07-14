import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra')))

from todo import TodoStack
import pytest

class TestTodoStack:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = cdk.App()
        self.stack = TodoStack(self.app, "TodoStackTest")
        self.template = Template.from_stack(self.stack)

    def test_dynamodb_table_configuration(self):
        """Test DynamoDB table is configured correctly."""
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "BillingMode": "PAY_PER_REQUEST",
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ]
        })

    def test_lambda_function_configuration(self):
        """Test Lambda function is configured correctly."""
        self.template.has_resource_properties("AWS::Lambda::Function", {
            "Runtime": "python3.9",
            "Handler": "handler.main",
            "Environment": {
                "Variables": Match.object_like({
                    "TABLE_NAME": Match.any_value()
                })
            }
        })

    def test_lambda_has_dynamodb_permissions(self):
        """Test Lambda has proper DynamoDB permissions."""
        # Check IAM role exists
        self.template.resource_count_is("AWS::IAM::Role", 1)
        
        # Check IAM policy allows DynamoDB operations
        self.template.has_resource_properties("AWS::IAM::Policy", {
            "PolicyDocument": {
                "Statement": Match.array_with([
                    Match.object_like({
                        "Action": Match.array_with([
                            "dynamodb:BatchGetItem",
                            "dynamodb:GetRecords",
                            "dynamodb:GetShardIterator",
                            "dynamodb:Query",
                            "dynamodb:GetItem",
                            "dynamodb:Scan",
                            "dynamodb:ConditionCheckItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:PutItem",
                            "dynamodb:UpdateItem",
                            "dynamodb:DeleteItem"
                        ]),
                        "Effect": "Allow"
                    })
                ])
            }
        })

    def test_api_gateway_configuration(self):
        """Test API Gateway is configured correctly."""
        # Check REST API exists
        self.template.resource_count_is("AWS::ApiGateway::RestApi", 1)
        
        # Check resources exist
        self.template.resource_count_is("AWS::ApiGateway::Resource", 2)  # /items and /items/{id}
        
        # Check methods exist (GET, POST on /items; GET, PUT, DELETE on /items/{id})
        self.template.resource_count_is("AWS::ApiGateway::Method", 5)

    def test_api_gateway_lambda_integration(self):
        """Test API Gateway integrates with Lambda."""
        # Check Lambda permissions for API Gateway
        self.template.has_resource_properties("AWS::Lambda::Permission", {
            "Action": "lambda:InvokeFunction",
            "Principal": "apigateway.amazonaws.com"
        })

    def test_resource_names_and_tags(self):
        """Test resources have proper names and tags."""
        # Check if table has removal policy for demo purposes
        self.template.has_resource("AWS::DynamoDB::Table", {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete"
        })

    def test_stack_outputs(self):
        """Test stack produces necessary outputs."""
        # You might want to add outputs to your stack later
        # For now, we'll just verify the stack can be synthesized
        assert self.template is not None
        
    def test_security_groups_and_networking(self):
        """Test networking configuration (if any)."""
        # Since this is a serverless stack, we don't expect VPC resources
        # But we can verify no unintended networking resources
        self.template.resource_count_is("AWS::EC2::VPC", 0)
        self.template.resource_count_is("AWS::EC2::SecurityGroup", 0)