"""
User APIのルートを定義するモジュール

プレフィックスは `/api/v1/auth` として `app.py` で登録されている
認証はJWTを使用
"""

from json import JSONDecodeError
from typing import Literal

from flask import Blueprint, Response, jsonify, request

from api.schemas.user import UserRegisterSchema, UserSchema
from api.services.user import UserService

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register() -> tuple[Response, Literal[201]]:
    """
    新しいユーザーを登録するエンドポイント
    """
    # JSONデータが存在するか確認
    if not request.is_json:
        return jsonify({"message": "JSONデータが必要です"}), 400

    # リクエストボディからJSONデータを取得
    user_data = request.get_json(force=True, silent=True)
    if request.get_data() is not None and user_data is None:
        msg = "JSONデータの解析に失敗しました"
        raise JSONDecodeError(msg, "", 0)

    # スキーマを使用してデータをバリデーション
    user_schema = UserRegisterSchema()
    validated_data = user_schema.load(user_data)
    # ユーザーサービスを使用してユーザーを登録
    user = UserService.register_user(validated_data)

    # スキーマを使用してデータをシリアライズ
    user_data = user_schema.dump(user)
    return jsonify(user_data), 201


@user_bp.route("/login", methods=["POST"])
def login() -> tuple[Response, Literal[200]]:
    """
    ユーザーをログインするエンドポイント
    """
    # JSONデータが存在するか確認
    if not request.is_json:
        return jsonify({"message": "JSONデータが必要です"}), 400

    # リクエストボディからJSONデータを取得
    try:
        user_data = request.get_json()
    except JSONDecodeError:
        return jsonify({"message": "無効なJSONデータです"}), 400

    # スキーマを使用してデータをバリデーション
    user_schema = UserSchema()
    validated_data = user_schema.load(user_data)
    # ユーザーサービスを使用してユーザーをログイン
    # user = UserService.login_user(validated_data)

    # スキーマを使用してデータをシリアライズ
    user_data = user_schema.dump(validated_data)
    return jsonify(user_data), 200


@user_bp.route("/refresh", methods=["POST"])
def refresh() -> tuple[Response, Literal[200]]:
    """
    アクセストークンをリフレッシュするエンドポイント
    """
    # JSONデータが存在するか確認
    if not request.is_json:
        return jsonify({"message": "JSONデータが必要です"}), 400

    # リクエストボディからJSONデータを取得
    try:
        refresh_data = request.get_json()
    except JSONDecodeError:
        return jsonify({"message": "無効なJSONデータです"}), 400

    # スキーマを使用してデータをバリデーション
    user_schema = UserSchema()
    validated_data = user_schema.load(refresh_data)
    # ユーザーサービスを使用してアクセストークンをリフレッシュ
    # new_tokens = UserService.refresh_token(validated_data)

    # スキーマを使用してデータをシリアライズ
    tokens_data = user_schema.dump(validated_data)
    return jsonify(tokens_data), 200


@user_bp.route("/logout", methods=["POST"])
def logout() -> tuple[Response, Literal[200]]:
    """
    ユーザーをログアウトするエンドポイント
    """
    # JSONデータが存在するか確認
    if not request.is_json:
        return jsonify({"message": "JSONデータが必要です"}), 400

    # リクエストボディからJSONデータを取得
    try:
        logout_data = request.get_json()
    except JSONDecodeError:
        return jsonify({"message": "無効なJSONデータです"}), 400

    # スキーマを使用してデータをバリデーション
    user_schema = UserSchema()
    validated_data = user_schema.load(logout_data)
    # UserService.logout_user(validated_data)

    return jsonify({"message": "ログアウトしました"}), 200

@user_bp.route("/profile", methods=["GET"])
def profile() -> Response:
    """
    ユーザープロフィールを取得するエンドポイント
    """
    # ユーザー情報を取得
    # user = UserService.get_user_profile()
    # スキーマを使用してデータをシリアライズ
    user_schema = UserSchema()
    # user_data = user_schema.dump(user)
    return jsonify(user_schema)
