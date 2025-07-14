import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
import json
import handler

class TestHandler:
    def test_list_items(self, mocker):
        mock_table = mocker.patch("handler.table.scan", return_value={"Items": [{"id": "1", "title": "Test"}]})
        response = handler.list_items()
        assert response["statusCode"] == 200
        assert "Test" in response["body"]

    def test_create_item(self, mocker):
        mocker.patch("handler.table.put_item", return_value=None)
        event = {
            "body": json.dumps({"title": "New Todo", "description": "Test desc"})
        }
        response = handler.create_item(event)
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "New Todo"

    def test_get_item_found(self, mocker):
        mocker.patch("handler.table.get_item", return_value={"Item": {"id": "1", "title": "A"}})
        event = {"pathParameters": {"id": "1"}}
        response = handler.get_item(event)
        assert response["statusCode"] == 200

    def test_get_item_not_found(self, mocker):
        mocker.patch("handler.table.get_item", return_value={})
        event = {"pathParameters": {"id": "999"}}
        response = handler.get_item(event)
        assert response["statusCode"] == 404

    def test_update_item(self, mocker):
        mocker.patch("handler.table.update_item", return_value=None)
        event = {
            "pathParameters": {"id": "1"},
            "body": json.dumps({"title": "Updated", "done": True})
        }
        response = handler.update_item(event)
        assert response["statusCode"] == 200

    def test_delete_item(self, mocker):
        mocker.patch("handler.table.delete_item", return_value=None)
        event = {"pathParameters": {"id": "1"}}
        response = handler.delete_item(event)
        assert response["statusCode"] == 204

    def test_main_get_all_items(self, mocker):
        mocker.patch("handler.table.scan", return_value={"Items": [{"id": "1", "title": "Test"}]})
        event = {"httpMethod": "GET"}
        response = handler.main(event, {})
        assert response["statusCode"] == 200

    def test_main_get_single_item(self, mocker):
        mocker.patch("handler.table.get_item", return_value={"Item": {"id": "1", "title": "Test"}})
        event = {
            "httpMethod": "GET",
            "pathParameters": {"id": "1"}
        }
        response = handler.main(event, {})
        assert response["statusCode"] == 200

    def test_main_create_item(self, mocker):
        mocker.patch("handler.table.put_item", return_value=None)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"title": "New Todo", "description": "Test desc"})
        }
        response = handler.main(event, {})
        assert response["statusCode"] == 201

    def test_main_update_item(self, mocker):
        mocker.patch("handler.table.update_item", return_value=None)
        event = {
            "httpMethod": "PUT",
            "pathParameters": {"id": "1"},
            "body": json.dumps({"title": "Updated", "done": True})
        }
        response = handler.main(event, {})
        assert response["statusCode"] == 200

    def test_main_delete_item(self, mocker):
        mocker.patch("handler.table.delete_item", return_value=None)
        event = {
            "httpMethod": "DELETE",
            "pathParameters": {"id": "1"}
        }
        response = handler.main(event, {})
        assert response["statusCode"] == 204

    def test_main_unsupported_method(self, mocker):
        event = {"httpMethod": "PATCH"}
        response = handler.main(event, {})
        assert response["statusCode"] == 400
        assert "Unsupported method" in response["body"]