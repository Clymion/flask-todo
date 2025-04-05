"""
PUT /todos/{id} エンドポイントのテスト
"""

import pytest
from flask import json
from datetime import datetime, timedelta


class TestUpdateTodo:
    """ToDo更新エンドポイントのテストクラス"""

    def test_update_single_field(self, test_client, setup_sample_todos):
        """単一フィールドの更新が正常に行われることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"title": "更新されたタイトル"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == todo_id
        assert data["title"] == update_data["title"]
        # 元の値が維持されていることを確認
        assert data["description"] == setup_sample_todos[0]["description"]
        assert data["priority"] == setup_sample_todos[0]["priority"]
        assert data["status"] == setup_sample_todos[0]["status"]

    def test_update_multiple_fields(self, test_client, setup_sample_todos):
        """複数フィールドの更新が正常に行われることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {
            "title": "更新されたタイトル",
            "description": "更新された説明",
            "priority": "low",
            "status": "completed",
        }

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == todo_id
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["priority"] == update_data["priority"]
        assert data["status"] == update_data["status"]

    def test_updated_at_is_updated(self, test_client, setup_sample_todos):
        """更新時にupdated_atが更新されることを確認"""
        todo_id = setup_sample_todos[0]["id"]
        original_updated_at = setup_sample_todos[0]["updated_at"]

        # 少し待ってから更新
        import time

        time.sleep(0.1)

        update_data = {"title": "新しいタイトル"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        # updated_atが変更されているか確認
        assert data["updated_at"] != original_updated_at

    def test_created_at_not_changed(self, test_client, setup_sample_todos):
        """更新時にcreated_atが変更されないことを確認"""
        todo_id = setup_sample_todos[0]["id"]
        original_created_at = setup_sample_todos[0]["created_at"]

        update_data = {"title": "新しいタイトル"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        # created_atは変更されないはず
        assert data["created_at"] == original_created_at

    def test_update_nonexistent_todo(self, test_client):
        """存在しないIDのToDoの更新に対して404エラーが返されることを確認"""
        nonexistent_id = 9999

        update_data = {"title": "存在しないToDoの更新"}

        response = test_client.update_todo(nonexistent_id, update_data)
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['code'] == 404
        assert 'message' in data

    def test_update_with_invalid_id_format(self, test_client):
        """無効なID形式での更新に対して400エラーが返されることを確認"""
        invalid_id = "abc"

        update_data = {"title": "無効なIDの更新"}

        response = test_client.client.put(
            f"/api/v1/todos/{invalid_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'id' in data['errors']

    def test_update_with_empty_title(self, test_client, setup_sample_todos):
        """空のタイトルでの更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"title": ""}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'title' in data['errors']

    def test_update_with_title_too_long(self, test_client, setup_sample_todos):
        """タイトルが長すぎる更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"title": "a" * 101}  # 101文字

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'title' in data['errors']

    def test_update_with_description_too_long(self, test_client, setup_sample_todos):
        """説明が長すぎる更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"description": "a" * 501}  # 501文字

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'description' in data['errors']

    def test_update_with_invalid_priority(self, test_client, setup_sample_todos):
        """無効な優先度での更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"priority": "invalid_priority"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'priority' in data['errors']

    def test_update_with_invalid_status(self, test_client, setup_sample_todos):
        """無効なステータスでの更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"status": "invalid_status"}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'status' in data['errors']

    def test_update_with_invalid_due_date_format(self, test_client, setup_sample_todos):
        """無効な期限日形式での更新に対して400エラーが返されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"due_date": "2023/04/04"}  # 不正な形式

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 400

        # data = json.loads(response.data)
        # assert 'errors' in data
        # assert 'due_date' in data['errors']

    def test_update_with_duplicate_title(self, test_client, setup_sample_todos):
        """他のToDoと重複するタイトルでの更新に対して409エラーが返されることを確認"""
        # 1つ目のToDoを取得
        todo_id = setup_sample_todos[0]["id"]

        # 2つ目のToDoのタイトルで更新しようとする
        update_data = {"title": setup_sample_todos[1]["title"]}

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 409

        # data = json.loads(response.data)
        # assert data['code'] == 409
        # assert 'message' in data

    def test_update_with_same_title(self, test_client, setup_sample_todos):
        """同じToDoの現在のタイトルでの更新が正常に処理されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        # 同じタイトルで更新
        update_data = {
            "title": setup_sample_todos[0]["title"],
            "description": "説明だけ変更",
        }

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["title"] == setup_sample_todos[0]["title"]
        assert data["description"] == update_data["description"]

    def test_update_with_boundary_title_length(self, test_client, setup_sample_todos):
        """ちょうど100文字のタイトルでの更新が正常に処理されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"title": "a" * 100}  # ちょうど100文字

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["title"]) == 100

    def test_update_with_boundary_description_length(
        self, test_client, setup_sample_todos
    ):
        """ちょうど500文字の説明での更新が正常に処理されることを確認"""
        todo_id = setup_sample_todos[0]["id"]

        update_data = {"description": "a" * 500}  # ちょうど500文字

        response = test_client.update_todo(todo_id, update_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["description"]) == 500
