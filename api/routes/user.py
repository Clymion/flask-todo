"""
User APIのルートを定義するモジュール

プレフィックスは `/api/v1/auth` として `app.py` で登録されている
認証はJWTを使用
"""

from json import JSONDecodeError
from typing import Literal

from flask import Blueprint, Response, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from api.schemas.user import UserLoginSchema, UserRegisterSchema, UserSchema
from api.services.user import UserService
from api.utils.init_jwt import REDIS_JWT_EXPIRES, jwt_blocklist

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
    user_data = request.get_json(force=True, silent=True)
    if request.get_data() is not None and user_data is None:
        msg = "JSONデータの解析に失敗しました"
        raise JSONDecodeError(msg, "", 0)

    # スキーマを使用してデータをバリデーション
    user_schema = UserLoginSchema()
    validated_data = user_schema.load(user_data)
    # ユーザーサービスを使用してユーザーをログイン
    user = UserService.login_user(validated_data)

    # スキーマを使用してデータをシリアライズ
    user_data = user_schema.dump(user)
    if user_data is None:
        return jsonify({"message": "ユーザーが見つかりません"}), 404

    # トークンを生成
    access_token = create_access_token(identity=str(user_data["id"]), fresh=True)
    refresh_token = create_refresh_token(identity=str(user_data["id"]))
    response = jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        },
    )
    return response, 200


@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> tuple[Response, Literal[200]]:
    """
    アクセストークンをリフレッシュするエンドポイント

    リフレッシュトークンを受け取って、トークンレスポンスを返す
    """
    # ユーザー情報を取得
    current_user_id: int = get_jwt_identity()

    # トークンを生成
    access_token = create_access_token(identity=current_user_id, fresh=False)
    refresh_token = create_refresh_token(identity=current_user_id)
    response = jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        },
    )
    return response, 200


@user_bp.route("/logout", methods=["POST"])
@jwt_required(verify_type=False)
def logout() -> tuple[Response, Literal[200]]:
    """
    ユーザーをログアウトするエンドポイント
    """
    # JWT IDを取得して、トークンを無効化
    token = get_jwt()
    jti = token["jti"]
    ttype: str | None = token["type"]
    jwt_blocklist.set(jti, "", ex=REDIS_JWT_EXPIRES)

    return (
        jsonify(
            {
                "message": "ログアウトしました",
                "ttype": f"{ttype.capitalize()} token revoked",
            },
        ),
        200,
    )


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile() -> Response:
    """
    ユーザープロフィールを取得するエンドポイント
    """
    # ユーザー情報を取得
    current_user_id: int = get_jwt_identity()
    user = UserService.get_user_by_id(current_user_id)
    # スキーマを使用してデータをシリアライズ
    user_schema = UserSchema()
    user_data = user_schema.dump(user)
    return jsonify(user_data), 200
