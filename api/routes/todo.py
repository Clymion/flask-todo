"""
ToDo APIのルートを定義するモジュール

プレフィックスは `/api/v1/todo` として `app.py` で登録されている
"""

from json import JSONDecodeError
from typing import Literal

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.schemas.todo import TodoQuerySchema, TodoSchema
from api.services.todo import TodoService

todo_bp = Blueprint("todos", __name__)


@todo_bp.route("/", methods=["GET"])
@jwt_required()
def get() -> Response:
    """
    ToDoリストを取得するエンドポイント
    """
    # クエリパラメータを取得
    status = request.args.get("status")
    priority = request.args.get("priority")
    due_before = request.args.get("due_before")
    due_after = request.args.get("due_after")
    user_id = get_jwt_identity()

    # クエリパラメータのバリデーション
    todo_query_schema = TodoQuerySchema()
    validated_params = todo_query_schema.load(
        {
            "status": status,
            "priority": priority,
            "due_before": due_before,
            "due_after": due_after,
            "user_id": user_id,
        },
    )

    # ToDoServiceを使用してデータを取得
    todos = TodoService.get_all_todos(
        status=validated_params.get("status"),
        priority=validated_params.get("priority"),
        due_before=validated_params.get("due_before"),
        due_after=validated_params.get("due_after"),
        user_id=validated_params.get("user_id"),
    )
    # スキーマを使用してデータをシリアライズ
    todo_schema = TodoSchema(many=True)
    todos_data = todo_schema.dump(todos)
    # レスポンスを返す
    return jsonify(todos_data)


@todo_bp.route("/", methods=["POST"])
@jwt_required()
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

    # ユーザーIDをJWTから取得して追加
    user_id = get_jwt_identity()
    data["user_id"] = user_id

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
@jwt_required()
def get_by_id(todo_id: int) -> Response:
    """
    IDによってToDoアイテムを取得するエンドポイント
    """
    user_id = get_jwt_identity()
    params = {
        "id": todo_id,
        "user_id": user_id,
    }
    # バリデーション
    query_schema = TodoQuerySchema()
    validated_params = query_schema.load(params)
    # ToDoServiceを使用してデータを取得
    todo = TodoService.get_todo_by_id(
        todo_id=validated_params.get("id"),
        user_id=validated_params.get("user_id"),
    )
    # スキーマを使用してデータをシリアライズ
    todo_schema = TodoSchema()
    todo_data = todo_schema.dump(todo)
    # レスポンスを返す
    return jsonify(todo_data)


@todo_bp.route("/<todo_id>", methods=["PUT"])
@jwt_required()
def update(todo_id: int) -> Response:
    """
    IDによってToDoアイテムを更新するエンドポイント
    """
    # IDのバリデーション
    user_id = get_jwt_identity()
    params = {
        "id": todo_id,
        "user_id": user_id,
    }
    query_schema = TodoQuerySchema()
    validated_params = query_schema.load(params)

    # JSONデータが存在するか確認
    if not request.is_json:
        msg = "リクエストボディにJSONデータがありません"
        raise JSONDecodeError(msg, "", 0)

    # JSONデータを解析
    json_data = request.get_json(force=True, silent=True)
    if request.get_data() is not None and json_data is None:
        msg = "JSONデータの解析に失敗しました"
        raise JSONDecodeError(msg, "", 0)
    if "user_id" not in json_data:
        json_data["user_id"] = user_id

    # スキーマを使用してデータをバリデーション
    todo_schema = TodoSchema()
    todo_data = todo_schema.load(json_data)

    # ToDoServiceを使用してデータを更新
    todo = TodoService.update_todo(
        validated_params.get("id"), validated_params.get("user_id"), todo_data,
    )
    # スキーマを使用してデータをシリアライズ
    todo_data = todo_schema.dump(todo)
    # レスポンスを返す
    return jsonify(todo_data)


@todo_bp.route("/<todo_id>", methods=["DELETE"])
@jwt_required()
def delete(todo_id: int) -> Response:
    """
    IDによってToDoアイテムを削除するエンドポイント
    """
    # IDのバリデーション
    user_id = get_jwt_identity()
    params = {
        "id": todo_id,
        "user_id": user_id,
    }
    query_schema = TodoQuerySchema()
    validated_params = query_schema.load(params)

    # ToDoServiceを使用してデータを削除
    TodoService.delete_todo(validated_params.get("id"), validated_params.get("user_id"))
    # レスポンスを返す
    return "", 204
