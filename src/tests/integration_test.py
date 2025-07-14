import requests
import json
import pytest
import time
import os
import uuid
from typing import Dict, Any, List

class TestTodoAPIIntegration:
    """
    True integration tests that hit the actual deployed API Gateway.
    These are blackbox tests - we only care about inputs and outputs.
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Get API URL from environment or CDK outputs
        self.api_base_url = self._get_api_url()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Skip if API URL is not available
        if not self.api_base_url:
            pytest.skip("API_BASE_URL not set - skipping integration tests")
        
        # Store created items for cleanup
        self.created_items: List[str] = []
        
        print(f"🔗 Testing API at: {self.api_base_url}")

    def teardown_method(self):
        """Clean up any items created during tests."""
        for item_id in self.created_items:
            try:
                self._delete_item(item_id)
            except:
                pass  # Ignore cleanup errors

    def _get_api_url(self) -> str:
        """Get API URL from environment or CDK outputs."""
        # First try environment variable
        api_url = os.environ.get('API_BASE_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # Try to read from CDK outputs file
        try:
            with open('cdk-outputs-test.json', 'r') as f:
                outputs = json.load(f)
            
            # Look for API URL in outputs
            for stack_name, stack_outputs in outputs.items():
                # Now it will find "TodoApiUrl" ✅
                if 'TodoApiUrl' in stack_outputs:
                    return stack_outputs['TodoApiUrl'].rstrip('/')
        except:
            pass
        
        return None

    def _delete_item(self, item_id: str):
        """Helper to delete an item."""
        response = requests.delete(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers
        )
        return response

    def test_api_is_accessible(self):
        """Test that the API is accessible and returns a valid response."""
        response = requests.get(
            f"{self.api_base_url}/items",
            headers=self.headers,
            timeout=30
        )
        
        # Should return 200 (with items) or 200 (empty list)
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('application/json')
        
        # Should return a valid JSON array
        items = response.json()
        assert isinstance(items, list)
        
        print(f"✅ API is accessible, returned {len(items)} items")

    def test_create_todo_item(self):
        """Test creating a single todo item."""
        todo_data = {
            "title": "Integration Test Todo",
            "description": "Created by integration test",
            "done": False
        }
        
        response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(todo_data),
            timeout=30
        )
        
        assert response.status_code == 201
        assert response.headers.get('content-type', '').startswith('application/json')
        
        created_item = response.json()
        
        # Verify response structure
        assert 'id' in created_item
        assert created_item['title'] == todo_data['title']
        assert created_item['description'] == todo_data['description']
        assert created_item['done'] == todo_data['done']
        assert isinstance(created_item['id'], str)
        assert len(created_item['id']) > 0
        
        # Track for cleanup
        self.created_items.append(created_item['id'])
        
        print(f"✅ Created item with ID: {created_item['id']}")

    def test_get_todo_item(self):
        """Test retrieving a specific todo item."""
        # First create an item
        todo_data = {
            "title": "Get Test Todo",
            "description": "For testing GET endpoint",
            "done": True
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(todo_data),
            timeout=30
        )
        
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item['id']
        self.created_items.append(item_id)
        
        # Now get the item
        get_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert get_response.status_code == 200
        assert get_response.headers.get('content-type', '').startswith('application/json')
        
        retrieved_item = get_response.json()
        
        # Verify the retrieved item matches what we created
        assert retrieved_item['id'] == item_id
        assert retrieved_item['title'] == todo_data['title']
        assert retrieved_item['description'] == todo_data['description']
        assert retrieved_item['done'] == todo_data['done']
        
        print(f"✅ Retrieved item: {retrieved_item['title']}")

    def test_update_todo_item(self):
        """Test updating a todo item."""
        # Create an item
        original_data = {
            "title": "Original Title",
            "description": "Original Description",
            "done": False
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(original_data),
            timeout=30
        )
        
        created_item = create_response.json()
        item_id = created_item['id']
        self.created_items.append(item_id)
        
        # Update the item
        updated_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "done": True
        }
        
        update_response = requests.put(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            data=json.dumps(updated_data),
            timeout=30
        )
        
        assert update_response.status_code == 200
        
        # Verify the update by getting the item again
        get_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert get_response.status_code == 200
        updated_item = get_response.json()
        
        assert updated_item['id'] == item_id
        assert updated_item['title'] == updated_data['title']
        assert updated_item['description'] == updated_data['description']
        assert updated_item['done'] == updated_data['done']
        
        print(f"✅ Updated item: {updated_item['title']}")

    def test_delete_todo_item(self):
        """Test deleting a todo item."""
        # Create an item
        todo_data = {
            "title": "To Be Deleted",
            "description": "This item will be deleted",
            "done": False
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(todo_data),
            timeout=30
        )
        
        created_item = create_response.json()
        item_id = created_item['id']
        
        # Delete the item
        delete_response = requests.delete(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert delete_response.status_code == 204
        
        # Verify deletion by trying to get the item
        get_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert get_response.status_code == 404
        
        print(f"✅ Deleted item with ID: {item_id}")

    def test_list_multiple_items(self):
        """Test listing multiple todo items."""
        # Create multiple items
        items_to_create = [
            {"title": "First Todo", "description": "Description 1", "done": False},
            {"title": "Second Todo", "description": "Description 2", "done": True},
            {"title": "Third Todo", "description": "Description 3", "done": False}
        ]
        
        created_ids = []
        for item_data in items_to_create:
            response = requests.post(
                f"{self.api_base_url}/items",
                headers=self.headers,
                data=json.dumps(item_data),
                timeout=30
            )
            
            assert response.status_code == 201
            created_item = response.json()
            created_ids.append(created_item['id'])
            self.created_items.append(created_item['id'])
        
        # List all items
        list_response = requests.get(
            f"{self.api_base_url}/items",
            headers=self.headers,
            timeout=30
        )
        
        assert list_response.status_code == 200
        items = list_response.json()
        assert isinstance(items, list)
        
        # Verify our created items are in the list
        returned_ids = [item['id'] for item in items]
        for created_id in created_ids:
            assert created_id in returned_ids
        
        print(f"✅ Listed {len(items)} items, including our {len(created_ids)} created items")

    def test_full_crud_workflow(self):
        """Test complete CRUD workflow in sequence."""
        # CREATE
        todo_data = {
            "title": "CRUD Workflow Test",
            "description": "Testing complete CRUD workflow",
            "done": False
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(todo_data),
            timeout=30
        )
        
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item['id']
        self.created_items.append(item_id)
        
        # READ
        read_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert read_response.status_code == 200
        read_item = read_response.json()
        assert read_item['title'] == todo_data['title']
        
        # UPDATE
        update_data = {
            "title": "Updated CRUD Test",
            "description": "Updated via CRUD workflow",
            "done": True
        }
        
        update_response = requests.put(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            data=json.dumps(update_data),
            timeout=30
        )
        
        assert update_response.status_code == 200
        
        # Verify update
        verify_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        verified_item = verify_response.json()
        assert verified_item['title'] == update_data['title']
        assert verified_item['done'] == update_data['done']
        
        # DELETE
        delete_response = requests.delete(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert delete_response.status_code == 204
        
        # Verify deletion
        final_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert final_response.status_code == 404
        
        print("✅ Complete CRUD workflow successful")

    def test_error_scenarios(self):
        """Test error handling scenarios."""
        # Test getting non-existent item
        non_existent_id = str(uuid.uuid4())
        get_response = requests.get(
            f"{self.api_base_url}/items/{non_existent_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert get_response.status_code == 404
        
        # Test updating non-existent item
        update_data = {"title": "Updated", "done": True}
        update_response = requests.put(
            f"{self.api_base_url}/items/{non_existent_id}",
            headers=self.headers,
            data=json.dumps(update_data),
            timeout=30
        )
        
        assert update_response.status_code in [404, 400]  # Depends on implementation
        
        # Test invalid JSON
        invalid_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data="invalid json",
            timeout=30
        )
        
        assert invalid_response.status_code in [400, 500]
        
        print("✅ Error scenarios handled correctly")

    def test_api_response_times(self):
        """Test API response times are reasonable."""
        # Test GET /items performance
        start_time = time.time()
        response = requests.get(
            f"{self.api_base_url}/items",
            headers=self.headers,
            timeout=30
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 5.0  # Should respond within 5 seconds
        
        print(f"✅ GET /items responded in {response_time:.2f}s")

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_item(thread_id):
            try:
                todo_data = {
                    "title": f"Concurrent Test {thread_id}",
                    "description": f"Created by thread {thread_id}",
                    "done": False
                }
                
                response = requests.post(
                    f"{self.api_base_url}/items",
                    headers=self.headers,
                    data=json.dumps(todo_data),
                    timeout=30
                )
                
                results.put({
                    'thread_id': thread_id,
                    'status_code': response.status_code,
                    'success': response.status_code == 201,
                    'item_id': response.json().get('id') if response.status_code == 201 else None
                })
                
            except Exception as e:
                results.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'success': False
                })
        
        # Create 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_item, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        successful_requests = 0
        created_ids = []
        
        while not results.empty():
            result = results.get()
            if result.get('success'):
                successful_requests += 1
                if result.get('item_id'):
                    created_ids.append(result['item_id'])
                    self.created_items.append(result['item_id'])
        
        # All requests should succeed
        assert successful_requests == 5
        assert len(created_ids) == 5
        
        print(f"✅ Successfully handled {successful_requests} concurrent requests")

    def test_data_persistence(self):
        """Test that data persists between requests."""
        # Create an item
        todo_data = {
            "title": "Persistence Test",
            "description": "Testing data persistence",
            "done": False
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/items",
            headers=self.headers,
            data=json.dumps(todo_data),
            timeout=30
        )
        
        created_item = create_response.json()
        item_id = created_item['id']
        self.created_items.append(item_id)
        
        # Wait a moment
        time.sleep(1)
        
        # Get the item again to verify it persisted
        get_response = requests.get(
            f"{self.api_base_url}/items/{item_id}",
            headers=self.headers,
            timeout=30
        )
        
        assert get_response.status_code == 200
        retrieved_item = get_response.json()
        
        assert retrieved_item['id'] == item_id
        assert retrieved_item['title'] == todo_data['title']
        assert retrieved_item['description'] == todo_data['description']
        assert retrieved_item['done'] == todo_data['done']
        
        print("✅ Data persistence verified")