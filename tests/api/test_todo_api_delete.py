"""
DELETE /todos/{id} エンドポイントのテスト
"""

from flask import json

from tests.conftest import TestClient


class TestDeleteTodo:
    """ToDo削除エンドポイントのテストクラス"""

    def test_delete_existing_todo(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """存在するToDoが正常に削除できることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        # ToDo削除
        response = test_client.delete_todo(todo_id, headers=auth_headers)
        assert response.status_code == 204
        assert response.data == b""  # 空のレスポンスボディ

        # 削除されたToDoが取得できないことを確認
        get_response = test_client.get_todo_by_id(todo_id, headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_nonexistent_todo(self, test_client: TestClient, auth_headers: dict):
        """存在しないIDのToDoの削除に対して404エラーが返されることを確認"""
        nonexistent_id = 9999

        response = test_client.delete_todo(nonexistent_id, headers=auth_headers)
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["code"] == 404
        assert "message" in data

    def test_delete_with_invalid_id_format(
        self, test_client: TestClient, auth_headers: dict,
    ):
        """無効なID形式での削除に対して400エラーが返されることを確認"""
        invalid_id = "abc"

        response = test_client.client.delete(
            f"/api/v1/todos/{invalid_id}", headers=auth_headers,
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "id" in data["errors"]

    def test_delete_with_negative_id(self, test_client: TestClient, auth_headers: dict):
        """負のIDでの削除に対して400エラーが返されることを確認"""
        negative_id = -1

        response = test_client.delete_todo(negative_id, headers=auth_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "id" in data["errors"]

    def test_delete_with_zero_id(self, test_client: TestClient, auth_headers: dict):
        """IDが0の削除に対して400エラーが返されることを確認"""
        zero_id = 0

        response = test_client.delete_todo(zero_id, headers=auth_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "id" in data["errors"]

    def test_multiple_delete_operations(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """同じIDの削除を複数回行った場合、最初は成功し、2回目以降は404エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        # 1回目の削除 (成功するはず)
        response1 = test_client.delete_todo(todo_id, headers=auth_headers)
        assert response1.status_code == 204

        # 2回目の削除 (404になるはず)
        response2 = test_client.delete_todo(todo_id, headers=auth_headers)
        assert response2.status_code == 404

        data = json.loads(response2.data)
        assert data["code"] == 404
        assert "message" in data

    def test_unauthorized_todo_deletion(
        self, test_client: TestClient, setup_sample_todos: list,
    ):
        """認証なしでToDo削除を試みると401エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]
        response = test_client.delete_todo(todo_id)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data
