"""
ユーザープロファイル取得のテスト: /auth/profile エンドポイント
"""

from typing import Any

from flask import json

from tests.conftest import TestClient


class TestUserProfile:
    """ユーザープロファイル取得エンドポイントのテストクラス"""

    def test_get_profile_success(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
        test_user: dict[str, Any],
    ):
        """認証済みのユーザーが自分のプロファイル情報を取得できることを確認"""
        response = test_client.get_user_profile(auth_header)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == test_user["id"]
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "created_at" in data
        # パスワードが含まれていないことを確認
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_profile_without_auth(self, test_client: TestClient):
        """認証なしでプロファイル情報を取得しようとした場合に401エラーが返されることを確認"""
        response = test_client.get_user_profile({})
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_get_profile_with_invalid_token(self, test_client: TestClient):
        """無効なトークンでプロファイル情報を取得しようとした場合に401エラーが返されることを確認"""
        invalid_auth_header = {"Authorization": "Bearer invalid.token.here"}
        response = test_client.get_user_profile(invalid_auth_header)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_get_profile_with_malformed_auth_header(self, test_client: TestClient):
        """不正な形式の認証ヘッダーでプロファイル情報を取得しようとした場合に401エラーが返されることを確認"""
        # Bearerプレフィックスがない
        malformed_header1 = {"Authorization": "invalid_token_format"}
        response1 = test_client.get_user_profile(malformed_header1)
        assert response1.status_code == 401

        # 空のトークン
        malformed_header2 = {"Authorization": "Bearer "}
        response2 = test_client.get_user_profile(malformed_header2)
        assert response2.status_code == 401

    def test_profile_contains_all_required_fields(
        self,
        test_client: TestClient,
        auth_header: dict[str, str],
    ):
        """プロファイル情報に必要なフィールドがすべて含まれていることを確認"""
        response = test_client.get_user_profile(auth_header)
        assert response.status_code == 200

        data = json.loads(response.data)
        # 必須フィールドの確認
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "created_at" in data

        # 型の確認
        assert isinstance(data["id"], int)
        assert isinstance(data["username"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["created_at"], str)
