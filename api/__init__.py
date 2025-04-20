"""
Flaskアプリケーションのファクトリ関数を定義するモジュール"""

import os

from flask import Flask

from api.routes.healthcheck import healthcheck_bp
from api.routes.swagger import swaggerui_bp
from api.routes.todo import todo_bp
from api.routes.user import user_bp
from api.utils.database import init_db
from api.utils.error_handlers import register_error_handlers
from api.utils.init_jwt import init_jwt


def create_app(config=None) -> Flask:
    """
    Flaskアプリケーションのインスタンスを作成するファクトリ関数

    Args:
        config: アプリケーションの設定 (オプション)

    Returns:
        Flaskアプリケーションインスタンス

    """
    app = Flask(__name__)
    app.json.ensure_ascii = False

    if config:
        app.config.update(config)

    app = init_jwt(app)

    # Blueprintを登録して、ルーティングを設定
    app.register_blueprint(swaggerui_bp)
    app.register_blueprint(healthcheck_bp, url_prefix="/")
    app.register_blueprint(todo_bp, url_prefix="/api/v1/todos")
    app.register_blueprint(user_bp, url_prefix="/api/v1/auth")

    # エラーハンドラーを登録
    register_error_handlers(app)

    # データベースの初期化
    if not app.config.get("TESTING"):
        init_db(app)

    return app


DEFAULT_PORT = 5000

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=os.environ.get("PORT", DEFAULT_PORT))
