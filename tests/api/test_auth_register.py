"""
ユーザー登録のテスト: /auth/register エンドポイント
"""

from typing import Any

from flask import json

from tests.conftest import TestClient


class TestUserRegister:
    """ユーザー登録エンドポイントのテストクラス"""

    def test_register_user_success(self, test_client: TestClient):
        """有効なユーザー情報で正常に登録できることを確認"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!",
        }

        response = test_client.register_user(user_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "id" in data
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data  # パスワードが含まれていないことを確認
        assert "created_at" in data

    def test_register_with_missing_fields(self, test_client: TestClient):
        """必須項目が欠けている場合に400エラーが返されることを確認"""
        # usernameが欠けている
        user_data1 = {"email": "test@example.com", "password": "Password123!"}
        response1 = test_client.register_user(user_data1)
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert "errors" in data1
        assert "username" in data1["errors"]

        # emailが欠けている
        user_data2 = {"username": "testuser", "password": "Password123!"}
        response2 = test_client.register_user(user_data2)
        assert response2.status_code == 400
        data2 = json.loads(response2.data)
        assert "errors" in data2
        assert "email" in data2["errors"]

        # passwordが欠けている
        user_data3 = {"username": "testuser", "email": "test@example.com"}
        response3 = test_client.register_user(user_data3)
        assert response3.status_code == 400
        data3 = json.loads(response3.data)
        assert "errors" in data3
        assert "password" in data3["errors"]

    def test_register_with_invalid_username_length(self, test_client: TestClient):
        """ユーザー名の長さが無効な場合に400エラーが返されることを確認"""
        # 短すぎるユーザー名 (3文字未満)
        short_username_data = {
            "username": "ab",  # 2文字
            "email": "test@example.com",
            "password": "Password123!",
        }
        response1 = test_client.register_user(short_username_data)
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert "errors" in data1
        assert "username" in data1["errors"]

        # 長すぎるユーザー名 (50文字超)
        long_username_data = {
            "username": "a" * 51,  # 51文字
            "email": "test@example.com",
            "password": "Password123!",
        }
        response2 = test_client.register_user(long_username_data)
        assert response2.status_code == 400
        data2 = json.loads(response2.data)
        assert "errors" in data2
        assert "username" in data2["errors"]

    def test_register_with_invalid_email_format(self, test_client: TestClient):
        """無効なメールアドレス形式でエラーが返されることを確認"""
        invalid_email_data = {
            "username": "testuser",
            "email": "invalid-email",  # @がない
            "password": "Password123!",
        }
        response = test_client.register_user(invalid_email_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "email" in data["errors"]

    def test_register_with_short_password(self, test_client: TestClient):
        """パスワードが短すぎる場合に400エラーが返されることを確認"""
        short_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Short1!",  # 7文字
        }
        response = test_client.register_user(short_password_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "password" in data["errors"]

    def test_register_with_duplicate_username(
        self, test_client: TestClient, test_user: dict[str, Any],
    ):
        """既存のユーザー名で登録しようとした場合に409エラーが返されることを確認"""
        duplicate_username_data = {
            "username": test_user["username"],  # 既存のユーザー名
            "email": "different@example.com",
            "password": "Password123!",
        }
        response = test_client.register_user(duplicate_username_data)
        assert response.status_code == 409
        data = json.loads(response.data)
        assert "message" in data
        assert "ユーザ" in data["message"]

    def test_register_with_duplicate_email(
        self, test_client: TestClient, test_user: dict[str, Any],
    ):
        """既存のメールアドレスで登録しようとした場合に409エラーが返されることを確認"""
        duplicate_email_data = {
            "username": "differentuser",
            "email": test_user["email"],  # 既存のメールアドレス
            "password": "Password123!",
        }
        response = test_client.register_user(duplicate_email_data)
        assert response.status_code == 409
        data = json.loads(response.data)
        assert "message" in data
        assert "メールアドレス" in data["message"].lower()

    def test_register_with_boundary_username_length(self, test_client: TestClient):
        """ちょうど3文字と50文字のユーザー名で正常に登録できることを確認"""
        # ちょうど3文字のユーザー名
        min_username_data = {
            "username": "abc",  # 3文字
            "email": "min@example.com",
            "password": "Password123!",
        }
        response1 = test_client.register_user(min_username_data)
        assert response1.status_code == 201
        data1 = json.loads(response1.data)
        assert data1["username"] == "abc"

        # ちょうど50文字のユーザー名
        max_username_data = {
            "username": "a" * 50,  # 50文字
            "email": "max@example.com",
            "password": "Password123!",
        }
        response2 = test_client.register_user(max_username_data)
        assert response2.status_code == 201
        data2 = json.loads(response2.data)
        assert len(data2["username"]) == 50

    def test_register_with_boundary_password_length(self, test_client: TestClient):
        """ちょうど8文字のパスワードで正常に登録できることを確認"""
        min_password_data = {
            "username": "pwdtest",
            "email": "pwd@example.com",
            "password": "Pass123!",  # ちょうど8文字
        }
        response = test_client.register_user(min_password_data)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data
        assert data["username"] == "pwdtest"
