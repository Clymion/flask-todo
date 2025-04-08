"""
Flaskアプリケーションのファクトリ関数を定義するモジュール"""

from flask import Flask

from api.routes.todo import todo_bp
from api.utils.database import init_db
from api.utils.error_handlers import register_error_handlers


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

    app.register_blueprint(todo_bp, url_prefix="/api/v1/todos")
    register_error_handlers(app)
    if not app.config.get("TESTING"):
        init_db(app)

    @app.route("/")
    def index() -> dict[str, str]:
        return {"index": "Hello World!"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
