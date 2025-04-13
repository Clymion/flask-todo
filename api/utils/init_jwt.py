"""初期化時にJWT設定をFlaskアプリケーションに設定するモジュール"""

from flask import Flask
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
