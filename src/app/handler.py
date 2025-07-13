import json
import os
import boto3
from model import TodoItem

TABLE_NAME = os.environ.get("TABLE_NAME", "TodoTable")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def main(event, context):
    method = event.get("httpMethod")
    if method == "GET":
        if event.get("pathParameters") and event["pathParameters"].get("id"):
            return get_item(event)
        else:
            return list_items()
    elif method == "POST":
        return create_item(event)
    elif method == "PUT":
        return update_item(event)
    elif method == "DELETE":
        return delete_item(event)
    else:
        return {"statusCode": 400, "body": json.dumps({"message": "Unsupported method"})}

def list_items():
    response = table.scan()
    return {"statusCode": 200, "body": json.dumps(response["Items"])}

def get_item(event):
    item_id = event["pathParameters"]["id"]
    response = table.get_item(Key={"id": item_id})
    item = response.get("Item")
    if item:
        return {"statusCode": 200, "body": json.dumps(item)}
    return {"statusCode": 404, "body": json.dumps({"message": "Not found"})}

def create_item(event):
    body = json.loads(event["body"])
    item = TodoItem(**body)
    table.put_item(Item=item.__dict__)
    return {"statusCode": 201, "body": json.dumps(item.__dict__)}

def update_item(event):
    item_id = event["pathParameters"]["id"]
    body = json.loads(event["body"])
    update_expression = "set title = :t, description = :d, done = :done"
    expr_values = {
        ":t": body["title"],
        ":d": body.get("description", ""),
        ":done": body["done"]
    }
    table.update_item(
        Key={"id": item_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expr_values
    )
    return {"statusCode": 200, "body": json.dumps({"message": "Updated"})}

def delete_item(event):
    item_id = event["pathParameters"]["id"]
    table.delete_item(Key={"id": item_id})
    return {"statusCode": 204, "body": ""}