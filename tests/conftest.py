"""
テスト用の共通フィクスチャとヘルパー関数を提供するモジュール
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest
from flask import Flask, json
from flask.testing import FlaskClient

# APIの実装をインポートする予定のためのプレースホルダー
from api import create_app
from api.utils.database import db


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
        }
    )

    # アプリケーションコンテキストを設定
    db.init_app(app)
    with app.app_context():
        # データベースを初期化
        db.create_all()
        pass

    yield app

    # テスト終了後にファイルをクローズして削除
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask):
    """テスト用のクライアントを提供するフィクスチャ"""
    return app.test_client()


@pytest.fixture
def todo_data():
    """基本的なToDoデータを提供するフィクスチャ"""
    return {
        "title": "テストタスク",
        "description": "これはテスト用のタスクです",
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
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
            "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "priority": "high",
            "status": "not_started",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
        {
            "id": 2,
            "title": "進行中のタスク",
            "description": "現在進行中のタスク",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "status": "in_progress",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
        {
            "id": 3,
            "title": "完了したタスク",
            "description": "既に完了したタスク",
            "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "priority": "low",
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    ]


@pytest.fixture
def setup_sample_todos(app: Flask, sample_todos):
    """
    テスト用のデータベースにサンプルToDoを登録するフィクスチャ

    実際の実装では、DBモデルを使用してデータを登録するが、
    今はプレースホルダーとしておく
    """
    with app.app_context():
        # 将来の実装のためのプレースホルダー
        # for todo_data in sample_todos:
        #     todo = Todo(
        #         title=todo_data['title'],
        #         description=todo_data['description'],
        #         due_date=datetime.strptime(todo_data['due_date'], '%Y-%m-%d').date() if todo_data.get('due_date') else None,
        #         priority=todo_data['priority'],
        #         status=todo_data['status']
        #     )
        #     db.session.add(todo)
        # db.session.commit()
        pass

    return sample_todos


class TestClient:
    """
    テスト用のHTTPクライアントユーティリティクラス
    APIリクエストを簡単に行うためのヘルパーメソッドを提供
    """

    def __init__(self, client: FlaskClient):
        self.client = client
        self.base_url = "/api/v1"

    def get_todos(self, query_params=None):
        """全ToDoリストを取得"""
        url = f"{self.base_url}/todos/"
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{url}?{query_string}"
        return self.client.get(url)

    def create_todo(self, todo_data):
        """新規ToDoを作成"""
        return self.client.post(
            f"{self.base_url}/todos/",
            data=json.dumps(todo_data),
            content_type="application/json",
        )

    def get_todo_by_id(self, todo_id):
        """IDによるToDo取得"""
        return self.client.get(f"{self.base_url}/todos/{todo_id}")

    def update_todo(self, todo_id, update_data):
        """ToDoを更新"""
        return self.client.put(
            f"{self.base_url}/todos/{todo_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

    def delete_todo(self, todo_id):
        """ToDoを削除"""
        return self.client.delete(f"{self.base_url}/todos/{todo_id}")


@pytest.fixture
def test_client(client):
    """拡張したテストクライアントを提供するフィクスチャ"""
    return TestClient(client)


# 日付関連のユーティリティ関数
def today_str():
    """今日の日付を文字列で返す"""
    return datetime.now().strftime("%Y-%m-%d")


def tomorrow_str():
    """明日の日付を文字列で返す"""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def yesterday_str():
    """昨日の日付を文字列で返す"""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
