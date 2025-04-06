"""
GET /todos/{id} エンドポイントのテスト
"""

from flask import json

from tests.conftest import TestClient


class TestGetTodoById:
    """ToDo取得エンドポイントのテストクラス"""

    def test_get_existing_todo(self, test_client: TestClient, setup_sample_todos):
        """存在するIDのToDoが正常に取得できることを確認"""
        # サンプルToDoの最初のアイテムのIDを使用
        todo_id = setup_sample_todos[0]["id"]

        response = test_client.get_todo_by_id(todo_id)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == todo_id
        assert data["title"] == setup_sample_todos[0]["title"]
        assert data["description"] == setup_sample_todos[0]["description"]
        assert data["priority"] == setup_sample_todos[0]["priority"]
        assert data["status"] == setup_sample_todos[0]["status"]
        assert "due_date" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_nonexistent_todo(self, test_client: TestClient):
        """存在しないIDのToDoに対して404エラーが返されることを確認"""
        # 存在しないIDを指定
        nonexistent_id = 9999

        response = test_client.get_todo_by_id(nonexistent_id)
        assert response.status_code == 404

        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data
        assert data["code"] == 404

    def test_get_todo_with_invalid_id_format(self, test_client: TestClient):
        """無効なID形式に対して400エラーが返されることを確認"""
        invalid_id = "abc"

        response = test_client.get_todo_by_id(invalid_id)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data
        assert "errors" in data
        assert "id" in data["errors"]

    def test_get_todo_with_negative_id(self, test_client):
        """負のIDに対して400エラーが返されることを確認"""
        negative_id = -1

        response = test_client.get_todo_by_id(negative_id)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "id" in data["errors"]

    def test_get_todo_with_zero_id(self, test_client):
        """IDが0の場合に400エラーが返されることを確認"""
        zero_id = 0

        response = test_client.get_todo_by_id(zero_id)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "id" in data["errors"]

    def test_get_todo_response_has_all_fields(self, test_client, setup_sample_todos):
        """レスポンスに全フィールドが含まれていることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        response = test_client.get_todo_by_id(todo_id)
        assert response.status_code == 200

        data = json.loads(response.data)
        # 全フィールドの存在確認
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "due_date" in data
        assert "priority" in data
        assert "status" in data
        assert "created_at" in data
        assert "updated_at" in data
