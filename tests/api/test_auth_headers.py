"""
認証ヘッダーの検証に関するテスト
"""

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from flask import json
from freezegun import freeze_time

from tests.conftest import TestClient


class TestAuthHeaders:
    """認証ヘッダーの検証に関するテストクラス"""

    def test_empty_auth_header(self, test_client: TestClient):
        """認証ヘッダーが空の場合に401エラーが返されることを確認"""
        # 保護されたエンドポイントにヘッダーなしでアクセス
        response = test_client.get_user_profile(headers={})
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data
        assert "token" in data["message"].lower() or "auth" in data["message"].lower()

    def test_invalid_auth_header_format(self, test_client: TestClient):
        """無効な形式のBearer認証ヘッダーの場合に401エラーが返されることを確認"""
        # Bearerプレフィックスがない
        invalid_header1 = {"Authorization": "invalid_token_format"}
        response1 = test_client.get_user_profile(headers=invalid_header1)
        assert response1.status_code == 401

        # 空のトークン
        invalid_header2 = {"Authorization": "Bearer "}
        response2 = test_client.get_user_profile(headers=invalid_header2)
        assert response2.status_code == 401

        # 形式が完全に異なる
        invalid_header3 = {"Authorization": "Basic dXNlcjpwYXNz"}  # Basic認証形式
        response3 = test_client.get_user_profile(headers=invalid_header3)
        assert response3.status_code == 401

    def test_expired_token(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """期限切れのアクセストークンで401エラーが返されることを確認"""
        auth_header = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # 現在日時を30日後に設定
        today_after_30_days = datetime.now(tz=ZoneInfo("Asia/Tokyo")) + timedelta(
            days=1,
        )
        with freeze_time(today_after_30_days.strftime("%Y-%m-%d %H:%M:%S")):
            response = test_client.get_user_profile(headers=auth_header)
            assert response.status_code == 401

            data = json.loads(response.data)
            assert "msg" in data
            assert "expire" in data["msg"].lower() or "期限" in data["msg"]

    def test_forged_token(self, test_client: TestClient):
        """偽造されたトークンで401エラーが返されることを確認"""
        # 有効なJWT形式だが署名が無効なトークン
        payload = {"sub": 1, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        forged_token = jwt.encode(payload, "wrong_secret_key", algorithm="HS256")

        auth_header = {"Authorization": f"Bearer {forged_token}"}
        response = test_client.get_user_profile(headers=auth_header)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert "message" in data
        assert "invalid" in data["message"].lower() or "fail" in data["message"]

    def test_invalid_token_signature(
        self,
        test_client: TestClient,
        auth_tokens: dict[str, str],
    ):
        """トークンの署名が無効な場合に401エラーが返されることを確認"""
        # 実際のトークンを改ざん
        parts = auth_tokens["access_token"].split(".")
        if len(parts) == 3:
            # ヘッダーとペイロードはそのまま、署名を改ざん
            tampered_token = f"{parts[0]}.{parts[1]}.invalidSignature"

            auth_header = {"Authorization": f"Bearer {tampered_token}"}
            response = test_client.get_user_profile(headers=auth_header)
            assert response.status_code == 401

            data = json.loads(response.data)
            assert "message" in data
            assert "signature" in data["message"].lower() or "署名" in data["message"]
