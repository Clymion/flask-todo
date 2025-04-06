"""
POST /todos エンドポイントのテスト
"""

from datetime import datetime

from flask import json

from tests.conftest import TestClient


class TestCreateTodo:
    """ToDo作成エンドポイントのテストクラス"""

    def test_create_todo_with_required_fields_only(self, test_client: TestClient):
        """必須フィールド (title)のみで新規ToDoが作成できることを確認"""
        todo_data = {"title": "タイトルのみのタスク"}

        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["title"] == todo_data["title"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # デフォルト値が正しく設定されていることを確認
        assert data["priority"] == "medium"
        assert data["status"] == "not_started"

    def test_create_todo_with_all_fields(self, test_client, todo_data):
        """すべてのフィールドを指定して新規ToDoが作成できることを確認"""
        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["due_date"] == todo_data["due_date"]
        assert data["priority"] == todo_data["priority"]
        assert data["status"] == todo_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_id_is_auto_assigned(self, test_client: TestClient, todo_data):
        """idが自動的に採番されることを確認"""
        # idフィールドを含める
        todo_with_id = todo_data.copy()
        todo_with_id["id"] = 999

        response = test_client.create_todo(todo_with_id)
        assert response.status_code == 201

        data = json.loads(response.data)
        # 指定したIDでなく自動採番されたIDであること
        assert data["id"] != todo_with_id["id"]

    def test_created_and_updated_at_are_set(self, test_client: TestClient, todo_data):
        """created_atとupdated_atが自動設定されることを確認"""
        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "created_at" in data
        assert "updated_at" in data

        # 日付形式の検証
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        # created_atとupdated_atは一致するはず (作成直後)
        assert created_at == updated_at

    def test_missing_title(self, test_client):
        """タイトルが欠落している場合にエラーが返されることを確認"""
        todo_data = {"description": "タイトルなしのタスク", "priority": "high"}

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'code' in data
        assert 'message' in data
        assert 'errors' in data
        assert 'title' in data['errors']

    def test_empty_title(self, test_client):
        """空のタイトルでエラーが返されることを確認"""
        todo_data = {"title": "", "description": "空のタイトル"}

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'title' in data['errors']

    def test_title_too_long(self, test_client):
        """タイトルが長すぎる場合にエラーが返されることを確認"""
        todo_data = {"title": "a" * 101, "description": "タイトルが長すぎる"}  # 101文字

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'title' in data['errors']

    def test_description_too_long(self, test_client):
        """説明が長すぎる場合にエラーが返されることを確認"""
        todo_data = {
            "title": "説明が長すぎるタスク",
            "description": "a" * 501,  # 501文字
        }

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'description' in data['errors']

    def test_invalid_priority(self, test_client):
        """無効な優先度でエラーが返されることを確認"""
        todo_data = {"title": "無効な優先度のタスク", "priority": "invalid_priority"}

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'priority' in data['errors']

    def test_invalid_status(self, test_client):
        """無効なステータスでエラーが返されることを確認"""
        todo_data = {"title": "無効なステータスのタスク", "status": "invalid_status"}

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'status' in data['errors']

    def test_invalid_due_date_format(self, test_client):
        """無効な期限日形式でエラーが返されることを確認"""
        todo_data = {
            "title": "無効な期限日のタスク",
            "due_date": "2023/04/04",  # 不正な形式
        }

        response = test_client.create_todo(todo_data)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'errors' in data
        assert 'due_date' in data['errors']

    def test_duplicate_title(self, test_client: TestClient, todo_data):
        """同一タイトルのToDoが既存のデータと重複する場合に409エラーが返されることを確認"""
        # 最初のToDoを作成
        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        # 同じタイトルで2回目のToDoを作成
        response = test_client.create_todo(todo_data)
        assert response.status_code == 409

        data = json.loads(response.data)
        assert data['code'] == 409
        assert 'message' in data

    def test_boundary_title_length(self, test_client):
        """ちょうど100文字のタイトルで正常に作成できることを確認"""
        todo_data = {
            "title": "a" * 100,  # ちょうど100文字
            "description": "ちょうど100文字のタイトル",
        }

        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert len(data["title"]) == 100

    def test_boundary_description_length(self, test_client):
        """ちょうど500文字の説明で正常に作成できることを確認"""
        todo_data = {
            "title": "長い説明のタスク",
            "description": "a" * 500,  # ちょうど500文字
        }

        response = test_client.create_todo(todo_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert len(data["description"]) == 500
