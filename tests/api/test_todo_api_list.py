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

    def test_get_all_todos(self, test_client: TestClient, setup_sample_todos):
        """全ToDoアイテムが正常に取得できることを確認"""
        response = test_client.get_todos()
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == len(setup_sample_todos)

    def test_filter_by_status(self, test_client: TestClient, setup_sample_todos):
        """statusパラメータによるフィルタリングが正常に機能することを確認"""
        # not_startedステータスのToDoのみを取得
        response = test_client.get_todos({"status": "not_started"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert all(todo["status"] == "not_started" for todo in data)
        assert len(data) == len(
            [t for t in setup_sample_todos if t["status"] == "not_started"],
        )

        # in_progressステータスのToDoのみを取得
        response = test_client.get_todos({"status": "in_progress"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["status"] == "in_progress" for todo in data)

        # completedステータスのToDoのみを取得
        response = test_client.get_todos({"status": "completed"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["status"] == "completed" for todo in data)

    def test_filter_by_priority(self, test_client: TestClient, setup_sample_todos):
        """priorityパラメータによるフィルタリングが正常に機能することを確認"""
        # lowプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "low"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "low" for todo in data)

        # mediumプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "medium"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "medium" for todo in data)

        # highプライオリティのToDoのみを取得
        response = test_client.get_todos({"priority": "high"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["priority"] == "high" for todo in data)

    def test_filter_by_due_date(self, test_client, setup_sample_todos):
        """due_beforeとdue_afterパラメータによるフィルタリングが正常に機能することを確認"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 今日以降が期限のToDoを取得
        response = test_client.get_todos({"due_after": today})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["due_date"] >= today for todo in data)

        # 今日以前が期限のToDoを取得
        response = test_client.get_todos({"due_before": today})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(todo["due_date"] <= today for todo in data)

    def test_combined_filters(self, test_client: TestClient, setup_sample_todos):
        """複数のフィルターを組み合わせたクエリが正常に機能することを確認"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 高優先度で未着手かつ今日以降が期限のToDoを取得
        response = test_client.get_todos(
            {"priority": "high", "status": "not_started", "due_after": today},
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

    def test_invalid_status_filter(self, test_client: TestClient):
        """無効なstatusパラメータに対して適切なエラーが返されることを確認"""
        response = test_client.get_todos({"status": "invalid_status"})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data
        assert data["code"] == 400
        assert "errors" in data
        assert "status" in data["errors"]

    def test_invalid_priority_filter(self, test_client: TestClient):
        """無効なpriorityパラメータに対して適切なエラーが返されることを確認"""
        response = test_client.get_todos({"priority": "invalid_priority"})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "priority" in data["errors"]

    def test_invalid_date_format(self, test_client: TestClient):
        """無効な日付形式に対して適切なエラーが返されることを確認"""
        response = test_client.get_todos({"due_before": "not-a-date"})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "due_before" in data["errors"]

        response = test_client.get_todos({"due_after": "2023/01/01"})  # 不正な形式
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "errors" in data
        assert "due_after" in data["errors"]

    def test_performance_with_many_todos(self, test_client: TestClient, app):
        """大量のToDoがある場合のパフォーマンスを確認"""
        # 多数のToDoを作成
        with app.app_context():
            for i in range(100):
                todo = Todo(
                    title=f"Task {i}",
                    description=f"Description for task {i}",
                    priority="medium",
                    status="not_started",
                )
                db.session.add(todo)
            db.session.commit()
            pass

        # パフォーマンスの確認
        import time

        start_time = time.time()
        response = test_client.get_todos()
        end_time = time.time()

        assert response.status_code == 200
        # レスポンスタイムが許容範囲内か確認 (例: 500ms以内)
        assert end_time - start_time < 0.5
