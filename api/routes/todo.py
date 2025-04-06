"""
ToDo APIのルートを定義するモジュール

プレフィックスは `/api/v1/todo` として `app.py` で登録されている
"""

import json
from typing import Literal

from flask import Blueprint, Response, jsonify, request

from api.schemas.todo import TodoQuerySchema, TodoSchema
from api.services.todo import TodoService

todo_bp = Blueprint("todos", __name__)


@todo_bp.route("/", methods=["GET"])
def get() -> Response:
    """
    ToDoリストを取得するエンドポイント
    """
    # クエリパラメータを取得
    status = request.args.get("status")
    priority = request.args.get("priority")
    due_before = request.args.get("due_before")
    due_after = request.args.get("due_after")

    # クエリパラメータのバリデーション
    todo_query_schema = TodoQuerySchema()
    validated_params = todo_query_schema.load(
        {
            "status": status,
            "priority": priority,
            "due_before": due_before,
            "due_after": due_after,
        },
    )

    # ToDoServiceを使用してデータを取得
    todos = TodoService.get_all_todos(
        status=validated_params.get("status"),
        priority=validated_params.get("priority"),
        due_before=validated_params.get("due_before"),
        due_after=validated_params.get("due_after"),
    )
    # スキーマを使用してデータをシリアライズ
    todo_schema = TodoSchema(many=True)
    todos_data = todo_schema.dump(todos)
    # レスポンスを返す
    return jsonify(todos_data)


@todo_bp.route("/", methods=["POST"])
def create() -> tuple[Response, Literal[201]]:
    """
    新しいToDoアイテムを作成するエンドポイント
    """
    # JSONデータが存在するか確認
    if not request.is_json:
        msg = "リクエストボディにJSONデータがありません"
        raise json.JSONDecodeError(msg, "", 0)

    # JSONデータを解析
    # force=True はリクエストのContent-Typeが application/json でなくても解析を試みる
    try:
        # silent=False を指定すると、JSONデコードエラー発生時に例外を投げる
        data = request.get_json(force=True, silent=False)
        if data is None:
            msg = "JSONデータが空です"
            raise json.JSONDecodeError(msg, "", 0)
    except Exception as e:
        # 標準のJSONDecodeErrorではなくても、JSONDecodeErrorに変換して投げる
        if not isinstance(e, json.JSONDecodeError):
            msg = f"JSONの解析に失敗しました: {e!s}"
            raise json.JSONDecodeError(msg, "", 0)
        raise

    if "id" in data:
        # idフィールドは自動採番されるため、リクエストボディから削除
        del data["id"]

    # スキーマを使用してデータをバリデーション
    todo_schema = TodoSchema()

    todo_data = todo_schema.load(data)
    # ToDoServiceを使用してデータを保存
    todo = TodoService.create_todo(todo_data)
    # スキーマを使用してデータをシリアライズ
    todo_data = todo_schema.dump(todo)
    # レスポンスを返す
    return jsonify(todo_data), 201
