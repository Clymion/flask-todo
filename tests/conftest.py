"""
テスト用の共通フィクスチャとヘルパー関数を提供するモジュール
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from flask import Flask, json
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash
from werkzeug.test import TestResponse

from api import create_app
from api.models.todo import Todo
from api.models.user import User
from api.utils.database import db

JST = ZoneInfo("Asia/Tokyo")  # 日本標準時 (JST) のタイムゾーン情報を取得


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションインスタンスを提供するフィクスチャ"""
    # 一時的なデータベースファイルを作成
    db_fd, db_path = tempfile.mkstemp()

    app: Flask = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            # JWT設定を追加
            "JWT_SECRET_KEY": "test-secret-key",
            "JWT_ACCESS_TOKEN_EXPIRES": 3600,  # 1時間
            "JWT_REFRESH_TOKEN_EXPIRES": 604800,  # 7日間
        },
    )

    # アプリケーションコンテキストを設定
    db.init_app(app)
    with app.app_context():
        # データベースを初期化
        db.create_all()

    yield app

    # テスト終了後にファイルをクローズして削除
    os.close(db_fd)
    Path.unlink(db_path)


@pytest.fixture
def client(app: Flask):
    """テスト用のクライアントを提供するフィクスチャ"""
    return app.test_client()


@pytest.fixture
def test_user_data() -> dict[str, str]:
    """テスト用のユーザーデータを提供するフィクスチャ"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def test_user(app: Flask, test_user_data: dict[str, str]) -> dict[str, Any]:
    """テストユーザーを作成し、そのユーザー情報を返すフィクスチャ"""
    with app.app_context():
        # 既存のユーザーがある場合は削除
        User.query.filter_by(username=test_user_data["username"]).delete()
        User.query.filter_by(email=test_user_data["email"]).delete()
        db.session.commit()

        # テストユーザーを作成
        user = User(
            username=test_user_data["username"],
            email=test_user_data["email"],
            password=test_user_data["password"],
        )
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": test_user_data["password"],
        }


@pytest.fixture
def test_users(app: Flask) -> list[dict[str, Any]]:
    """複数のテストユーザーを作成するフィクスチャ"""
    users_data = [
        {"username": "user1", "email": "user1@example.com", "password": "Password1!"},
        {"username": "user2", "email": "user2@example.com", "password": "Password2!"},
    ]

    created_users = []

    with app.app_context():
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
            )
            db.session.add(user)
            db.session.flush()

            created_users.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "password": user_data["password"],
                },
            )

        db.session.commit()

    return created_users


@pytest.fixture
def auth_tokens(client: FlaskClient, test_user: dict[str, Any]) -> dict[str, str]:
    """認証トークンを取得するフィクスチャ"""
    login_data = {"username": test_user["username"], "password": test_user["password"]}

    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps(login_data),
        content_type="application/json",
    )

    data = json.loads(response.data)

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture
def auth_header(auth_tokens: dict[str, str]) -> dict[str, str]:
    """認証ヘッダーを提供するフィクスチャ"""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}


@pytest.fixture
def auth_token(client: FlaskClient, test_user: dict) -> str:
    """認証トークンを取得するフィクスチャ"""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps(login_data),
        content_type="application/json",
    )
    data = json.loads(response.data)
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """認証ヘッダーを提供するフィクスチャ"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def multi_user_auth_tokens(
    client: FlaskClient,
    test_users: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """複数ユーザーの認証トークンを取得するフィクスチャ"""
    tokens = []

    for user in test_users:
        login_data = {"username": user["username"], "password": user["password"]}

        response = client.post(
            "/api/v1/auth/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        data = json.loads(response.data)

        tokens.append(
            {
                "user_id": user["id"],
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
            },
        )

    return tokens


@pytest.fixture
def todo_data():
    """基本的なToDoデータを提供するフィクスチャ"""
    return {
        "title": "テストタスク",
        "description": "これはテスト用のタスクです",
        "due_date": (datetime.now(tz=JST) + timedelta(days=7)).strftime("%Y-%m-%d"),
        "priority": "medium",
        "status": "not_started",
    }


@pytest.fixture
def sample_todos():
    """テスト用のToDoデータセットを提供するフィクスチャ"""
    return [
        {
            "id": 1,
            "title": "重要なタスク",
            "description": "最優先で取り組むべきタスク",
            "due_date": (datetime.now(tz=JST) + timedelta(days=1)).strftime("%Y-%m-%d"),
            "priority": "high",
            "status": "not_started",
            "created_at": datetime.fromtimestamp(1743462620.1, tz=JST),
            "updated_at": datetime.fromtimestamp(1743462620.1, tz=JST),
        },
        {
            "id": 2,
            "title": "進行中のタスク",
            "description": "現在進行中のタスク",
            "due_date": (datetime.now(tz=JST) + timedelta(days=3)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "status": "in_progress",
            "created_at": datetime.fromtimestamp(1743462620.2, tz=JST),
            "updated_at": datetime.fromtimestamp(1743462620.2, tz=JST),
        },
        {
            "id": 3,
            "title": "完了したタスク",
            "description": "既に完了したタスク",
            "due_date": (datetime.now(tz=JST) - timedelta(days=1)).strftime("%Y-%m-%d"),
            "priority": "low",
            "status": "completed",
            "created_at": datetime.fromtimestamp(1743462620.3, tz=JST),
            "updated_at": datetime.fromtimestamp(1743462620.3, tz=JST),
        },
    ]


@pytest.fixture
def setup_sample_todos(
    app: Flask,
    test_user: dict[str, Any],
    sample_todos: list[dict[str, Any]],
):
    """
    テスト用のデータベースにサンプルToDoを登録するフィクスチャ
    """
    with app.app_context():
        for todo_data in sample_todos:
            todo = Todo(
                title=todo_data["title"],
                description=todo_data["description"],
                due_date=(
                    datetime.strptime(todo_data["due_date"], "%Y-%m-%d").date()
                    if todo_data.get("due_date")
                    else None
                ),
                priority=todo_data["priority"],
                status=todo_data["status"],
                created_at=todo_data["created_at"],
                updated_at=todo_data["updated_at"],
                user_id=test_user["id"],  # ユーザーIDを関連付け
            )
            db.session.add(todo)
        db.session.commit()

    return sample_todos


@pytest.fixture
def setup_multi_user_todos(app: Flask, test_users: list[dict[str, Any]]):
    """複数ユーザーのToDoデータを設定するフィクスチャ"""
    todos_per_user = []

    with app.app_context():
        for user in test_users:
            user_todos = []

            # 各ユーザーに3つのToDoを作成
            for i in range(3):
                todo = Todo(
                    title=f"{user['username']}のタスク{i+1}",
                    description=f"{user['username']}のテスト用タスク{i+1}",
                    due_date=(datetime.now(tz=JST) + timedelta(days=i + 1)).date(),
                    priority=["low", "medium", "high"][i % 3],
                    status=["not_started", "in_progress", "completed"][i % 3],
                    user_id=user["id"],
                )
                db.session.add(todo)
                db.session.flush()

                user_todos.append(
                    {"id": todo.id, "title": todo.title, "user_id": user["id"]},
                )

            todos_per_user.append({"user_id": user["id"], "todos": user_todos})

        db.session.commit()

    return todos_per_user


class TestClient:
    """
    テスト用のHTTPクライアントユーティリティクラス

    APIリクエストを簡単に行うためのヘルパーメソッドを提供
    """

    def __init__(self, client: FlaskClient) -> None:
        """コンストラクタ"""
        self.client = client
        self.base_url = "/api/v1"

    def get_todos(
        self,
        query_params: dict[str, str] | None = None,
        headers: dict | None = None,
    ) -> TestResponse:
        """全ToDoリストを取得"""
        url = f"{self.base_url}/todos/"
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{url}?{query_string}"
        return self.client.get(url, headers=headers)

    def create_todo(self, todo_data: dict, headers: dict | None = None) -> TestResponse:
        """新規ToDoを作成"""
        return self.client.post(
            f"{self.base_url}/todos/",
            data=json.dumps(todo_data),
            content_type="application/json",
            headers=headers,
        )

    def get_todo_by_id(self, todo_id: int, headers: dict | None = None) -> TestResponse:
        """IDによるToDo取得"""
        return self.client.get(f"{self.base_url}/todos/{todo_id}", headers=headers)

    def update_todo(
        self,
        todo_id: int,
        update_data: dict,
        headers: dict | None = None,
    ) -> TestResponse:
        """ToDoを更新"""
        return self.client.put(
            f"{self.base_url}/todos/{todo_id}",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=headers,
        )

    def delete_todo(self, todo_id: int, headers: dict | None = None) -> TestResponse:
        """ToDoを削除"""
        return self.client.delete(f"{self.base_url}/todos/{todo_id}", headers=headers)

    # 認証関連のメソッドを追加
    def register_user(self, user_data: dict[str, str]) -> TestResponse:
        """ユーザー登録"""
        return self.client.post(
            f"{self.base_url}/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )

    def login_user(self, credentials: dict[str, str]) -> TestResponse:
        """ユーザーログイン"""
        return self.client.post(
            f"{self.base_url}/auth/login",
            data=json.dumps(credentials),
            content_type="application/json",
        )

    def refresh_token(
        self,
        refresh_token: str,
        headers: dict[str, str] | None = {},
    ) -> TestResponse:
        """トークン更新: リフレッシュトークンをヘッダーに含める"""
        headers["Authorization"] = f"Bearer {refresh_token}"
        return self.client.post(
            f"{self.base_url}/auth/refresh",
            content_type="application/json",
            headers=headers,
        )

    def logout_user(self, headers: dict[str, str]) -> TestResponse:
        """ユーザーログアウト"""
        return self.client.post(f"{self.base_url}/auth/logout", headers=headers)

    def get_user_profile(self, headers: dict[str, str]) -> TestResponse:
        """ユーザープロファイル取得"""
        return self.client.get(f"{self.base_url}/auth/profile", headers=headers)


@pytest.fixture
def test_client(client) -> TestClient:
    """拡張したテストクライアントを提供するフィクスチャ"""
    return TestClient(client)


# 日付関連のユーティリティ関数
def today_str() -> str:
    """今日の日付を文字列で返す"""
    return datetime.now(tz=JST).strftime("%Y-%m-%d")


def tomorrow_str() -> str:
    """明日の日付を文字列で返す"""
    return (datetime.now(tz=JST) + timedelta(days=1)).strftime("%Y-%m-%d")


def yesterday_str() -> str:
    """昨日の日付を文字列で返す"""
    return (datetime.now(tz=JST) - timedelta(days=1)).strftime("%Y-%m-%d")
