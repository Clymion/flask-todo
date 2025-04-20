"""
GET /todos エンドポイントのテスト
"""

from datetime import datetime

from flask import json

from api.models.todo import Todo
from api.utils.database import db
from tests.conftest import TestClient


class TestGetTodos:
    """ToDoリスト取得エンドポイントのテストクラス"""

    def test_get_all_todos(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """全ToDoアイテムが正常に取得できることを確認"""
        response = test_client.get_todos(headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == len(setup_sample_todos)

    def test_filter_by_status(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """statusパラメータによるフィルタリングが正常に機能することを確認"""
        # not_startedステータスのToDoのみを取得
        response = test_client.get_todos(
            {"status": "not_started"}, headers=auth_headers,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert all(todo["status"] == "not_started" for todo in data)
        assert len(data) == len(
            [t for t in setup_sample_todos if t["status"] == "not_started"],
        )

        # in_progressステータスのToDoのみを取得
        response = test_client.get_todos(
            {"status": "in_progress"}, headers=auth_headers,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["status"] == "in_progress" for todo in data)

        # completedステータスのToDoのみを取得
        response = test_client.get_todos({"status": "completed"}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["status"] == "completed" for todo in data)

    def test_filter_by_priority(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """priorityパラメータによるフィルタリングが正常に機能することを確認"""
        # lowプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "low"}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "low" for todo in data)

        # mediumプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "medium"}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "medium" for todo in data)

        # highプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "high"}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "high" for todo in data)

    def test_filter_by_due_date(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """due_beforeとdue_afterパラメータによるフィルタリングが正常に機能することを確認"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 今日以降が期限のToDoを取得
        response = test_client.get_todos({"due_after": today}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["due_date"] >= today for todo in data)

        # 今日以前が期限のToDoを取得
        response = test_client.get_todos({"due_before": today}, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["due_date"] <= today for todo in data)

    def test_combined_filters(
        self, test_client: TestClient, setup_sample_todos: list, auth_headers: dict,
    ):
        """複数のフィルターを組み合わせたクエリが正常に機能することを確認"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 高優先度で未着手かつ今日以降が期限のToDoを取得
        response = test_client.get_todos(
            {"priority": "high", "status": "not_started", "due_after": today},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # すべてのフィルター条件を満たすことを確認
        assert all(
            todo["priority"] == "high"
            and todo["status"] == "not_started"
            and todo["due_date"] >= today
            for todo in data
        )

    def test_invalid_status_filter(self, test_client: TestClient, auth_headers: dict):
        """無効なstatusパラメータに対して適切なエラーが返されることを確認"""
        response = test_client.get_todos(
            {"status": "invalid_status"}, headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data
        assert data["code"] == 400
        assert "errors" in data
        assert "status" in data["errors"]

    def test_invalid_priority_filter(self, test_client: TestClient, auth_headers: dict):
        """無効なpriorityパラメータに対して適切なエラーが返されることを確認"""
        response = test_client.get_todos(
            {"priority": "invalid_priority"}, headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "priority" in data["errors"]

    def test_invalid_date_format(self, test_client: TestClient, auth_headers: dict):
        """無効な日付形式に対して適切なエラーが返されることを確認"""
        response = test_client.get_todos(
            {"due_before": "not-a-date"}, headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "due_before" in data["errors"]

        response = test_client.get_todos(
            {"due_after": "2023/01/01"}, headers=auth_headers,
        )  # 不正な形式
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "due_after" in data["errors"]

    def test_performance_with_many_todos(
        self, test_client: TestClient, app, auth_headers: dict, test_user: dict,
    ):
        """大量のToDoがある場合のパフォーマンスを確認"""
        # 多数のToDoを作成
        with app.app_context():
            for i in range(100):
                todo = Todo(
                    title=f"Task {i}",
                    description=f"Description for task {i}",
                    priority="medium",
                    status="not_started",
                    user_id=test_user["id"],  # ユーザーIDを設定
                )
                db.session.add(todo)
            db.session.commit()

        # パフォーマンスの確認
        import time

        start_time = time.time()
        response = test_client.get_todos(headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        # レスポンスタイムが許容範囲内か確認 (例: 500ms以内)
        assert end_time - start_time < 0.5

    def test_unauthorized_todos_retrieval(self, test_client: TestClient):
        """認証なしでToDoリスト取得を試みると401エラーが返されることを確認"""
        response = test_client.get_todos()
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["code"] == 401
        assert "message" in data
