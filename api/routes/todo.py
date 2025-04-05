"""
ToDo APIのルートを定義するモジュール
プレフィックスは `/api/v1/todo` として `app.py` で登録されている
"""

from flask import Blueprint, jsonify, request

from api.models.todo import Todo
from api.utils.database import init_db


todo_bp = Blueprint("todos", __name__)


@todo_bp.route("/", methods=["GET", "POST"])
def get():
    return jsonify({"todos": "Hello World!"})
