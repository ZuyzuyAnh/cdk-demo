import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# Add the infra directory to the Python path  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra')))

import pytest
import boto3
from moto import mock_dynamodb

# Mock environment variables for tests
os.environ["TABLE_NAME"] = "test-todo-table"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"