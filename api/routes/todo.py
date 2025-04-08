"""
ToDo APIのルートを定義するモジュール

プレフィックスは `/api/v1/todo` として `app.py` で登録されている
"""

from json import JSONDecodeError
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
        raise JSONDecodeError(msg, "", 0)

    # JSONデータを解析
    data = request.get_json(force=True, silent=True)
    if request.get_data() is not None and data is None:
        msg = "JSONデータの解析に失敗しました"
        raise JSONDecodeError(msg, "", 0)

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


@todo_bp.route("/<todo_id>", methods=["GET"])
def get_by_id(todo_id: int) -> Response:
    """
    IDによってToDoアイテムを取得するエンドポイント
    """
    # IDのバリデーション
    query_schema = TodoQuerySchema()
    validated_params = query_schema.load({"id": todo_id})
    # ToDoServiceを使用してデータを取得
    todo = TodoService.get_todo_by_id(validated_params.get("id"))
    # スキーマを使用してデータをシリアライズ
    todo_schema = TodoSchema()
    todo_data = todo_schema.dump(todo)
    # レスポンスを返す
    return jsonify(todo_data)


@todo_bp.route("/<todo_id>", methods=["PUT"])
def update(todo_id: int) -> Response:
    """
    IDによってToDoアイテムを更新するエンドポイント
    """
    # IDのバリデーション
    query_schema = TodoQuerySchema()
    validated_params = query_schema.load({"id": todo_id})

    # JSONデータが存在するか確認
    if not request.is_json:
        msg = "リクエストボディにJSONデータがありません"
        raise JSONDecodeError(msg, "", 0)

    # JSONデータを解析
    json_data = request.get_json(force=True, silent=True)
    if request.get_data() is not None and json_data is None:
        msg = "JSONデータの解析に失敗しました"
        raise JSONDecodeError(msg, "", 0)

    # スキーマを使用してデータをバリデーション
    todo_schema = TodoSchema()
    todo_data = todo_schema.load(json_data)

    # ToDoServiceを使用してデータを更新
    todo = TodoService.update_todo(validated_params.get("id"), todo_data)
    # スキーマを使用してデータをシリアライズ
    todo_data = todo_schema.dump(todo)
    # レスポンスを返す
    return jsonify(todo_data)
