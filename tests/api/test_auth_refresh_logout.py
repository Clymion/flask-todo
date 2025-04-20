"""
トークン更新とログアウトのテスト: /auth/refresh と /auth/logout エンドポイント
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import json
from freezegun import freeze_time

from tests.conftest import TestClient


class TestTokenRefresh:
    """トークン更新エンドポイントのテストクラス"""

    def test_refresh_token_success(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """有効なリフレッシュトークンで新しいアクセストークンが取得できることを確認"""
        response = test_client.refresh_token(auth_tokens["refresh_token"])
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"

        # 新しいトークンが以前のトークンと異なることを確認
        assert data["access_token"] != auth_tokens["access_token"]

    def test_refresh_with_invalid_token(self, test_client: TestClient):
        """無効なリフレッシュトークンでエラーが返されることを確認"""
        invalid_token = "invalid.refresh.token"
        response = test_client.refresh_token(invalid_token)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_refresh_with_missing_token(self, test_client: TestClient):
        """リフレッシュトークンが指定されていない場合に401エラーが返されることを確認"""
        response = test_client.client.post(
            "/api/v1/auth/refresh",
            content_type="application/json",
        )
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["message"] is not None
        assert data["message"] != ""

    def test_expired_refresh_token(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """期限切れのリフレッシュトークンでエラーが返されることを確認"""
        # 現在日時を30日後に設定
        today_after_30_days = datetime.now(tz=ZoneInfo("Asia/Tokyo")) + timedelta(days=30)
        with freeze_time(today_after_30_days.strftime("%Y-%m-%d %H:%M:%S")):
            response = test_client.refresh_token(auth_tokens["refresh_token"])
            assert response.status_code == 401

            data = json.loads(response.data)
            key = "message" if "message" in data else "msg"
            assert key in data
            assert "expire" in data[key].lower()

    def test_access_with_new_token(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """更新されたアクセストークンで保護されたリソースにアクセスできることを確認"""
        # トークンを更新
        refresh_response = test_client.refresh_token(auth_tokens["refresh_token"])
        assert refresh_response.status_code == 200

        refresh_data = json.loads(refresh_response.data)
        new_token = refresh_data["access_token"]

        # 新しいトークンで保護されたリソースにアクセス
        auth_header = {"Authorization": f"Bearer {new_token}"}
        profile_response = test_client.get_user_profile(auth_header)
        assert profile_response.status_code == 200


class TestLogout:
    """ログアウトエンドポイントのテストクラス"""

    def test_logout_success(self, test_client: TestClient, auth_header: dict[str, str]):
        """認証済みのユーザーが正常にログアウトできることを確認"""
        response = test_client.logout_user(auth_header)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "message" in data
        assert "loguot" in data["message"] or "ログアウト" in data["message"]

    def test_logout_without_auth(self, test_client: TestClient):
        """認証なしでログアウトしようとした場合に401エラーが返されることを確認"""
        response = test_client.logout_user({})
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert data["code"] == 401

    def test_token_invalidation_after_logout(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """ログアウト後に古いトークンが無効化されることを確認"""
        # まずログアウト
        auth_header = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        logout_response = test_client.logout_user(auth_header)
        assert logout_response.status_code == 200

        # 同じトークンで保護されたリソースにアクセスしようとする
        profile_response = test_client.get_user_profile(auth_header)
        assert profile_response.status_code == 401

        # リフレッシュトークンも無効化
        auth_header = {"Authorization": f"Bearer {auth_tokens['refresh_token']}"}
        logout_response = test_client.logout_user(auth_header)
        assert logout_response.status_code == 200

        # リフレッシュトークンも無効化されていることを確認
        refresh_response = test_client.refresh_token(auth_tokens["refresh_token"])
        assert refresh_response.status_code == 401
