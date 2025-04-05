"""
データベース接続の設定ファイル
"""

import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# プロジェクトのルートディレクトリからの相対パスでdata/app.dbを指定
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

# SQLAlchemyインスタンスの作成
db = SQLAlchemy()


def init_db(app: Flask):
    """
    Flaskアプリケーションにデータベース設定を適用

    Args:
        app: Flaskアプリケーションインスタンス
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # データベースをアプリケーションに初期化
    db.init_app(app)

    # アプリケーションコンテキスト内でデータベースの作成を確保
    with app.app_context():
        db.create_all()
