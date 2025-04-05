from flask import Flask

from api.routes.todo import todo_bp
from api.utils.error_handlers import register_error_handlers


def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.update(config)

    app.register_blueprint(todo_bp, url_prefix="/api/v1/todos")
    register_error_handlers(app)

    @app.route("/")
    def index():
        return {"index": "Hello World!"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
