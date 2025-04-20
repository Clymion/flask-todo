"""
セキュリティ関連のテスト
"""

import re
from typing import Any

from flask import json

from tests.conftest import TestClient


class TestSecurity:
    """セキュリティ関連のテストクラス"""

    def test_password_not_returned(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """パスワードがレスポンスに含まれないことを確認"""
        # ユーザー登録時
        new_user_data = {
            "username": "securitytest",
            "email": "security@example.com",
            "password": "SecurePassword123!",
        }
        register_response = test_client.register_user(new_user_data)
        register_data = json.loads(register_response.data)

        assert "password" not in register_data
        assert "password_hash" not in register_data

        # ログイン時
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }
        login_response = test_client.login_user(login_data)
        login_data = json.loads(login_response.data)

        assert "password" not in login_data

        # プロファイル取得時
        auth_header = {"Authorization": f"Bearer {login_data['access_token']}"}
        profile_response = test_client.get_user_profile(auth_header)
        profile_data = json.loads(profile_response.data)

        assert "password" not in profile_data
        assert "password_hash" not in profile_data

    def test_error_messages_no_sensitive_info(self, test_client: TestClient):
        """エラーメッセージに機密情報が含まれていないことを確認"""
        # 無効なログイン試行
        login_data = {"username": "nonexistent", "password": "WrongPassword123!"}
        login_response = test_client.login_user(login_data)
        login_error = json.loads(login_response.data)

        # エラーメッセージに具体的なエラー内容(SQLクエリなど)が含まれていないことを確認
        assert not re.search(
            r"SQL|SELECT|INSERT|DELETE|UPDATE|DROP|CREATE|ALTER",
            login_error["message"],
            re.IGNORECASE,
        )

        # 無効なトークンでのアクセス
        invalid_auth_header = {"Authorization": "Bearer invalid.token.here"}
        profile_response = test_client.get_user_profile(invalid_auth_header)
        profile_error = json.loads(profile_response.data)

        # エラーメッセージにトークン内容や署名情報などが含まれていないことを確認
        assert not re.search(
            r"key|signature|algorithm|payload|secret",
            profile_error["message"],
            re.IGNORECASE,
        )

        # 存在しないToDoへのアクセス
        todo_response = test_client.get_todo_by_id(9999, headers=invalid_auth_header)
        todo_error = json.loads(todo_response.data)

        # エラーメッセージにデータベース情報が含まれていないことを確認
        assert not re.search(
            r"database|db|query|sql",
            todo_error["message"],
            re.IGNORECASE,
        )

    def test_sql_injection_username(self, test_client: TestClient):
        """SQLインジェクション攻撃への耐性があることを確認(ユーザー名)"""
        # SQLインジェクションを試みるユーザー名
        injection_login = {"username": "' OR 1=1 --", "password": "anypassword"}
        response = test_client.login_user(injection_login)

        # 成功せず401エラーが返されることを確認
        assert response.status_code == 401

    def test_sql_injection_todo_id(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """SQLインジェクション攻撃への耐性があることを確認(ToDoのID)"""
        # SQLインジェクションを試みるID
        injection_id = "1 OR 1=1"
        response = test_client.get_todo_by_id(injection_id, headers=auth_header)

        # 不正なIDとして扱われ400エラーが返されることを確認
        assert response.status_code == 400

    def test_token_contains_user_identifier(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """トークンにユーザー固有の識別子が含まれていることを確認"""
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }
        login_response = test_client.login_user(login_data)
        assert login_response.status_code == 200

        login_data = json.loads(login_response.data)
        auth_header = {"Authorization": f"Bearer {login_data['access_token']}"}

        # プロファイル情報を取得して、正しいユーザーの情報が返されることを確認
        profile_response = test_client.get_user_profile(auth_header)
        assert profile_response.status_code == 200

        profile_data = json.loads(profile_response.data)
        assert profile_data["id"] == test_user["id"]
        assert profile_data["username"] == test_user["username"]
