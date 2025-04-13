"""
ユーザーログインのテスト: /auth/login エンドポイント
"""

from typing import Any

from flask import json

from tests.conftest import TestClient


class TestUserLogin:
    """ユーザーログインエンドポイントのテストクラス"""

    def test_login_with_username_success(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """有効なユーザー名とパスワードで正常にログインできることを確認"""
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }

        response = test_client.login_user(login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"

    def test_login_with_email_success(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """有効なメールアドレスとパスワードで正常にログインできることを確認"""
        login_data = {
            "username": test_user["email"],  # ユーザー名の代わりにメールアドレスを使用
            "password": test_user["password"],
        }

        response = test_client.login_user(login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_with_nonexistent_user(self, test_client: TestClient):
        """存在しないユーザー名でログインしようとした場合に401エラーが返されることを確認"""
        login_data = {"username": "nonexistentuser", "password": "Password123!"}

        response = test_client.login_user(login_data)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_login_with_wrong_password(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """誤ったパスワードでログインしようとした場合に401エラーが返されることを確認"""
        login_data = {
            "username": test_user["username"],
            "password": "WrongPassword123!",
        }

        response = test_client.login_user(login_data)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_login_with_missing_fields(self, test_client: TestClient):
        """必須項目が欠けている場合に400エラーが返されることを確認"""
        # usernameが欠けている
        login_data1 = {"password": "Password123!"}
        response1 = test_client.login_user(login_data1)
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert "errors" in data1
        assert "username" in data1["errors"]

        # passwordが欠けている
        login_data2 = {"username": "testuser"}
        response2 = test_client.login_user(login_data2)
        assert response2.status_code == 400
        data2 = json.loads(response2.data)
        assert "errors" in data2
        assert "password" in data2["errors"]

    def test_token_contains_expiry(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """レスポンスに適切なトークン有効期限情報が含まれていることを確認"""
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }

        response = test_client.login_user(login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "expires_in" in data
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0  # 有効期限がプラスの値であることを確認

    def test_token_can_access_protected_resource(
        self,
        test_client: TestClient,
        test_user: dict[str, Any],
    ):
        """取得したトークンで保護されたリソースにアクセスできることを確認"""
        # ログインしてトークンを取得
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }

        login_response = test_client.login_user(login_data)
        assert login_response.status_code == 200

        login_data = json.loads(login_response.data)
        auth_header = {"Authorization": f"Bearer {login_data['access_token']}"}

        # 保護されたリソース(ユーザープロファイル)にアクセス
        profile_response = test_client.get_user_profile(auth_header)
        assert profile_response.status_code == 200

        profile_data = json.loads(profile_response.data)
        assert profile_data["username"] == test_user["username"]
        assert profile_data["email"] == test_user["email"]
