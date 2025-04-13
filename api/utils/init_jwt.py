"""初期化時にJWT設定をFlaskアプリケーションに設定するモジュール"""

from typing import Literal

from flask import Flask, jsonify
from flask.wrappers import Response
from flask_jwt_extended import JWTManager

from api.utils.config import settings

jwt = JWTManager()


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
def invalid_token_callback(error_string) -> tuple[Response, Literal[401]]:
    """
    JWTトークンが無効な場合のコールバック
    """
    return (
        jsonify({"code": 401, "message": "Authentication failed: " + error_string}),
        401,
    )
