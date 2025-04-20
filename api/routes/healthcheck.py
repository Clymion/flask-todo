"""
ヘルスチェック用のAPIエンドポイントを定義
"""

from flask import Blueprint, Response, jsonify

healthcheck_bp = Blueprint("healthcheck", __name__)

# 疎通確認用のルート
@healthcheck_bp.route("/", methods=["GET"])
def index() -> dict[str, str]:
    """疎通確認用のルート"""
    return {
        "message": "Welcome to the ToDo API!",
        "version": "1.0.0",
        "next_steps": [
            "1. ユーザー登録: POST /api/v1/auth/register/",
            "2. ログイン: POST /api/v1/auth/login/",
            "3. ToDoリストの取得: GET /api/v1/todos/",
            "4. ToDoアイテムの作成: POST /api/v1/todos/",
        ],
    }

# ヘルスチェック用のエンドポイント
@healthcheck_bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """ヘルスチェック用のエンドポイント"""
    return jsonify({"status": "ok"}), 200
