import aws_cdk as cdk
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
from constructs import Construct

class TodoStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        table = ddb.Table(
            self, "TodoTable",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,  # Add this line
            removal_policy=cdk.RemovalPolicy.DESTROY  # For demo purposes
        )

        # Lambda Function
        handler = _lambda.Function(
            self, "TodoHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.main",
            code=_lambda.Code.from_asset("src/app"),
            environment={
                "TABLE_NAME": table.table_name
            }
        )
        table.grant_full_access(handler)

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "TodoApi",
            handler=handler,
            proxy=False
        )

        items = api.root.add_resource("items")
        items.add_method("GET")    # list
        items.add_method("POST")   # create

        single = items.add_resource("{id}")
        single.add_method("GET")   # retrieve
        single.add_method("PUT")   # update
        single.add_method("DELETE") # delete

        cdk.CfnOutput(
            self, "TodoApiUrl",
            value=api.url,
            description="URL of the Todo API Gateway",
            export_name="TodoApiUrl"
        )
        
        # Optional: Also output the table name for debugging
        cdk.CfnOutput(
            self, "TodoTableName",
            value=table.table_name,
            description="Name of the DynamoDB table",
            export_name="TodoTableName"
        )