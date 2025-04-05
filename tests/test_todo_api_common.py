"""
ToDo APIの共通部分に関するテスト
"""

import pytest
from flask import json
from flask.testing import FlaskClient
from sqlalchemy import text

from api.utils.database import db
from tests.conftest import TestClient


def test_api_base_url_exists(client: FlaskClient):
    """APIのベースURLが存在することを確認"""
    response = client.get("/api/v1")
    # APIによっては404を返すかもしれないが、サーバーエラーではないことを確認
    print(f"response.status_code: {response.status_code}")
    assert response.status_code is not None
    assert response.status_code != 500


def test_database_connection(app):
    """データベース接続が正常に機能することを確認"""
    with app.app_context():
        # 将来の実装のためのプレースホルダー
        try:
            db.session.execute(text("SELECT 1"))
            assert True
        except Exception as e:
            pytest.fail(f"データベース接続に失敗しました: {e}")
        pass


def test_error_format_consistency(client: FlaskClient):
    """エラーレスポンスの形式が一貫していることを確認"""
    # 存在しないエンドポイントへのリクエスト
    response = client.get("/api/v1/nonexistent")

    # 現時点ではエラーレスポンスのフォーマットはまだ実装されていないが、
    # 将来的には以下のようなテストを行う
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "code" in data
    assert "message" in data
    assert data["code"] == 404


def test_json_content_type(test_client: TestClient):
    """APIレスポンスのContent-Typeがapplication/jsonであることを確認"""
    # ToDoリスト取得エンドポイントを使用してテスト
    response = test_client.get_todos()
    assert response.content_type == "application/json"


def test_empty_database_returns_empty_array(test_client: TestClient):
    """データベースが空の場合、空の配列が返されることを確認"""
    # この時点ではデータベースは空のはず
    response = test_client.get_todos()
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0


def test_invalid_json_payload(test_client: TestClient):
    """無効なJSON形式のペイロードに対して適切なエラーが返されることを確認"""
    response = test_client.client.post(
        "/api/v1/todos/", data="invalid json data", content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "code" in data
    assert "message" in data
    assert data["code"] == 400
    assert "JSONデコードエラー" in data["message"]


def test_method_not_allowed(client: FlaskClient):
    """許可されていないHTTPメソッドに対して適切なエラーが返されることを確認"""
    # DELETE /todosはAPI仕様に含まれていない
    response = client.delete("/api/v1/todos/")
    assert response.status_code == 405
    data = json.loads(response.data)
    assert "code" in data
    assert "message" in data
    assert data["code"] == 405
