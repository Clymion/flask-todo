"""初期化時にJWT設定をFlaskアプリケーションに設定するモジュール"""

from datetime import timedelta
from typing import Literal

import redis
from flask import Flask, jsonify
from flask.wrappers import Response
from flask_jwt_extended import JWTManager

from api.utils.config import settings

jwt = JWTManager()
jwt_blocklist = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)
REDIS_JWT_EXPIRES = timedelta(hours=1)


def init_jwt(app: Flask) -> Flask:
    """
    JWTManagerをFlaskアプリケーションに初期化する関数

    Args:
        app: Flaskアプリケーションインスタンス

    """
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY.get_secret_value()
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.JWT_REFRESH_TOKEN_EXPIRES
    jwt.init_app(app)
    return app


@jwt.invalid_token_loader
def invalid_token_callback(error_string: str) -> tuple[Response, Literal[401]]:
    """
    JWTトークンが無効な場合のコールバック
    """
    return (
        jsonify({"code": 401, "message": "Authentication failed: " + error_string}),
        401,
    )


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(_jwt_header: dict, jwt_payload: dict) -> bool:
    """
    JWTトークンがブロックリストにあるかどうかを確認する関数
    """
    jti = jwt_payload["jti"]
    token_in_redis = jwt_blocklist.get(jti)
    # トークンがブロックリストにある場合はTrueを返す (ある場合は、トークンが空文字で設定されている)
    return token_in_redis is not None
