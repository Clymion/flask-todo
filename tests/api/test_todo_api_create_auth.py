"""
POST /todos エンドポイントのテスト(認証対応版)
"""

from datetime import datetime
from typing import Any

from flask import json

from tests.conftest import TestClient


class TestCreateTodo:
    """ToDo作成エンドポイントのテストクラス(認証対応版)"""

    def test_create_todo_with_required_fields_only(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """必須フィールド (title)のみで新規ToDoが作成できることを確認"""
        todo_data = {"title": "タイトルのみのタスク"}

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["title"] == todo_data["title"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "user_id" in data  # ユーザーIDが設定されていることを確認

        # デフォルト値が正しく設定されていることを確認
        assert data["priority"] == "medium"
        assert data["status"] == "not_started"

    def test_create_todo_with_all_fields(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        auth_header: dict[str, str],
    ):
        """すべてのフィールドを指定して新規ToDoが作成できることを確認"""
        response = test_client.create_todo(todo_data, headers=auth_header)
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
        assert "user_id" in data

    def test_id_is_auto_assigned(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        auth_header: dict[str, str],
    ):
        """idが自動的に採番されることを確認"""
        # idフィールドを含める
        todo_with_id = todo_data.copy()
        todo_with_id["id"] = 999

        response = test_client.create_todo(todo_with_id, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        # 指定したIDでなく自動採番されたIDであること
        assert data["id"] != todo_with_id["id"]

    def test_created_and_updated_at_are_set(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        auth_header: dict[str, str],
    ):
        """created_atとupdated_atが自動設定されることを確認"""
        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "created_at" in data
        assert "updated_at" in data

        # 日付形式の検証
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        # created_atとupdated_atは秒単位で同じであることを確認
        assert created_at.year == updated_at.year
        assert created_at.month == updated_at.month
        assert created_at.day == updated_at.day
        assert created_at.hour == updated_at.hour
        assert created_at.minute == updated_at.minute
        assert created_at.second == updated_at.second
        assert (
            created_at.tzinfo == updated_at.tzinfo
        )  # タイムゾーンが同じであることを確認

    def test_user_id_is_set_to_current_user(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        auth_header: dict[str, str],
    ):
        """user_idが現在ログイン中のユーザーIDに設定されることを確認"""
        # 現在のユーザーのプロファイルを取得
        profile_response = test_client.get_user_profile(auth_header)
        profile_data = json.loads(profile_response.data)
        current_user_id = profile_data["id"]

        # ToDoを作成
        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "user_id" in data
        assert data["user_id"] == current_user_id

    def test_missing_title(self, test_client: TestClient, auth_header: dict[str, str]):
        """タイトルが欠落している場合にエラーが返されることを確認"""
        todo_data = {"description": "タイトルなしのタスク", "priority": "high"}

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data
        assert "errors" in data
        assert "title" in data["errors"]

    def test_empty_title(self, test_client: TestClient, auth_header: dict[str, str]):
        """空のタイトルでエラーが返されることを確認"""
        todo_data = {"title": "", "description": "空のタイトル"}

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "title" in data["errors"]

    def test_title_too_long(self, test_client: TestClient, auth_header: dict[str, str]):
        """タイトルが長すぎる場合にエラーが返されることを確認"""
        todo_data = {"title": "a" * 101, "description": "タイトルが長すぎる"}  # 101文字

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "title" in data["errors"]

    def test_description_too_long(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """説明が長すぎる場合にエラーが返されることを確認"""
        todo_data = {
            "title": "説明が長すぎるタスク",
            "description": "a" * 501,  # 501文字
        }

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "description" in data["errors"]

    def test_invalid_priority(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """無効な優先度でエラーが返されることを確認"""
        todo_data = {"title": "無効な優先度のタスク", "priority": "invalid_priority"}

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "priority" in data["errors"]

    def test_invalid_status(self, test_client: TestClient, auth_header: dict[str, str]):
        """無効なステータスでエラーが返されることを確認"""
        todo_data = {"title": "無効なステータスのタスク", "status": "invalid_status"}

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "status" in data["errors"]

    def test_invalid_due_date_format(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """無効な期限日形式でエラーが返されることを確認"""
        todo_data = {
            "title": "無効な期限日のタスク",
            "due_date": "2023/04/04",  # 不正な形式
        }

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "errors" in data
        assert "due_date" in data["errors"]

    def test_duplicate_title_for_same_user(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        auth_header: dict[str, str],
    ):
        """同一ユーザーで同一タイトルのToDoが既に存在する場合に409エラーが返されることを確認"""
        # 最初のToDoを作成
        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        # 同じタイトルで2回目のToDoを作成
        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 409

        data = json.loads(response.data)
        assert data["code"] == 409
        assert "message" in data

    def test_same_title_different_users(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
        multi_user_auth_tokens: dict[str, Any],
    ):
        """異なるユーザーが同じタイトルのToDoを作成できることを確認"""
        # ユーザー1でToDoを作成
        auth_header1 = {
            "Authorization": f"Bearer {multi_user_auth_tokens[0]['access_token']}",
        }
        response1 = test_client.create_todo(todo_data, headers=auth_header1)
        assert response1.status_code == 201

        # ユーザー2で同じタイトルのToDoを作成 (これは成功するはず)  # noqa: ERA001
        auth_header2 = {
            "Authorization": f"Bearer {multi_user_auth_tokens[1]['access_token']}",
        }
        response2 = test_client.create_todo(todo_data, headers=auth_header2)
        assert response2.status_code == 201

        # 2つのToDoが異なるユーザーIDを持つことを確認
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1["user_id"] != data2["user_id"]
        assert data1["title"] == data2["title"]

    def test_boundary_title_length(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """ちょうど100文字のタイトルで正常に作成できることを確認"""
        todo_data = {
            "title": "a" * 100,  # ちょうど100文字
            "description": "ちょうど100文字のタイトル",
        }

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert len(data["title"]) == 100

    def test_boundary_description_length(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """ちょうど500文字の説明で正常に作成できることを確認"""
        todo_data = {
            "title": "長い説明のタスク",
            "description": "a" * 500,  # ちょうど500文字
        }

        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert len(data["description"]) == 500
