"""
ToDoアイテムのアクセス制御に関するテスト
"""

from typing import Any

from flask import json

from tests.conftest import TestClient


class TestTodoAccessControl:
    """ToDoアイテムのアクセス制御に関するテストクラス"""

    def test_todo_list_only_returns_own_todos(
        self,
        test_client: TestClient,
        multi_user_auth_tokens: list[dict[str, str]],
        setup_multi_user_todos: list[dict[str, Any]],
    ):
        """認証済みユーザーが自分のToDoアイテムのみを取得できることを確認"""
        for i, user_tokens in enumerate(multi_user_auth_tokens):
            user_id = user_tokens["user_id"]
            auth_header = {"Authorization": f"Bearer {user_tokens['access_token']}"}

            # ユーザーのToDoリストを取得
            response = test_client.get_todos(headers=auth_header)
            assert response.status_code == 200

            todos = json.loads(response.data)
            assert isinstance(todos, list)

            # すべてのToDoが同じユーザーのものであることを確認
            for todo in todos:
                assert todo["user_id"] == user_id

            # 他のユーザーのToDoを含んでいないことを確認
            for other_user_data in setup_multi_user_todos:
                if other_user_data["user_id"] != user_id:
                    for other_todo in other_user_data["todos"]:
                        todo_ids = [t["id"] for t in todos]
                        assert other_todo["id"] not in todo_ids

    def test_get_todo_by_id_requires_auth(
        self,
        test_client: TestClient,
        setup_sample_todos: list[dict[str, Any]],
    ):
        """認証なしでToDoを取得しようとした場合に401エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]
        response = test_client.get_todo_by_id(todo_id)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data

    def test_get_another_users_todo_forbidden(
        self,
        test_client: TestClient,
        multi_user_auth_tokens: list[dict[str, str]],
        setup_multi_user_todos: list[dict[str, Any]],
    ):
        """他のユーザーのToDoを取得しようとした場合に403エラーが返されることを確認"""
        # ユーザー1のトークン
        user1_auth_header = {
            "Authorization": f"Bearer {multi_user_auth_tokens[0]['access_token']}",
        }

        # ユーザー2のToDo
        user2_todos = setup_multi_user_todos[1]["todos"]

        # ユーザー1がユーザー2のToDoにアクセスしようとする
        response = test_client.get_todo_by_id(
            user2_todos[0]["id"],
            headers=user1_auth_header,
        )
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["code"] == 404
        assert "message" in data

    def test_create_todo_requires_auth(
        self,
        test_client: TestClient,
        todo_data: dict[str, Any],
    ):
        """認証なしでToDoを作成しようとした場合に401エラーが返されることを確認"""
        response = test_client.create_todo(todo_data)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data

    def test_todo_creation_associates_with_user(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
        todo_data: dict[str, Any],
    ):
        """作成されたToDoに正しいユーザーIDが関連付けられていることを確認"""
        response = test_client.create_todo(todo_data, headers=auth_header)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "user_id" in data
        assert data["user_id"] is not None

        # プロファイル情報からユーザーIDを取得して比較
        profile_response = test_client.get_user_profile(auth_header)
        profile_data = json.loads(profile_response.data)

        assert data["user_id"] == profile_data["id"]

    def test_update_todo_requires_auth(
        self,
        test_client: TestClient,
        setup_sample_todos: list[dict[str, Any]],
    ):
        """認証なしでToDoを更新しようとした場合に401エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]
        update_data = {"title": "更新されたタイトル"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data

    def test_update_another_users_todo_forbidden(
        self,
        test_client: TestClient,
        multi_user_auth_tokens: list[dict[str, str]],
        setup_multi_user_todos: list[dict[str, Any]],
    ):
        """他のユーザーのToDoを更新しようとした場合に403エラーが返されることを確認"""
        # ユーザー1のトークン
        user1_auth_header = {
            "Authorization": f"Bearer {multi_user_auth_tokens[0]['access_token']}",
        }

        # ユーザー2のToDo
        user2_todos = setup_multi_user_todos[1]["todos"]

        # ユーザー1がユーザー2のToDoを更新しようとする
        update_data = {"title": "更新しようとしたタイトル"}
        response = test_client.update_todo(
            user2_todos[0]["id"],
            update_data,
            headers=user1_auth_header,
        )
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["code"] == 404
        assert "message" in data

    def test_delete_todo_requires_auth(
        self,
        test_client: TestClient,
        setup_sample_todos: list[dict[str, Any]],
    ):
        """認証なしでToDoを削除しようとした場合に401エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        response = test_client.delete_todo(todo_id)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data

    def test_delete_another_users_todo_forbidden(
        self,
        test_client: TestClient,
        multi_user_auth_tokens: list[dict[str, str]],
        setup_multi_user_todos: list[dict[str, Any]],
    ):
        """他のユーザーのToDoを削除しようとした場合に403エラーが返されることを確認"""
        # ユーザー1のトークン
        user1_auth_header = {
            "Authorization": f"Bearer {multi_user_auth_tokens[0]['access_token']}",
        }

        # ユーザー2のToDo
        user2_todos = setup_multi_user_todos[1]["todos"]

        # ユーザー1がユーザー2のToDoを削除しようとする
        response = test_client.delete_todo(
            user2_todos[0]["id"],
            headers=user1_auth_header,
        )
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["code"] == 404
        assert "message" in data

    def test_filter_applies_only_to_own_todos(
        self,
        test_client: TestClient,
        multi_user_auth_tokens: list[dict[str, str]],
        setup_multi_user_todos: list[dict[str, Any]],
    ):
        """フィルタリングが認証済みユーザーの自分のToDoに対してのみ適用されることを確認"""
        # ユーザー1のトークン
        user1_auth_header = {
            "Authorization": f"Bearer {multi_user_auth_tokens[0]['access_token']}",
        }

        # 特定のステータスでフィルタリング(例：completed)
        response = test_client.get_todos(
            {"status": "completed"},
            headers=user1_auth_header,
        )
        assert response.status_code == 200

        todos = json.loads(response.data)

        # 返されたすべてのToDoが条件を満たし、かつユーザー1のものであることを確認
        user1_id = multi_user_auth_tokens[0]["user_id"]
        for todo in todos:
            assert todo["status"] == "completed"
            assert todo["user_id"] == user1_id
