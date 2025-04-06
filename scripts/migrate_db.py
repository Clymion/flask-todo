"""
Todoテーブルを作成するためのマイグレーションスクリプト (一回限りの実行を想定)
"""

import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR.parent))

from flask import Flask

from api.models.todo import Todo
from api.utils.database import DB_PATH, db


def create_app_for_migration() -> Flask:
    """マイグレーション用のFlaskアプリケーションを作成"""
    app = Flask(__name__)

    # データベース設定
    os.makedirs(
        os.path.dirname(DB_PATH),
        exist_ok=True,
    )  # data ディレクトリが存在しない場合は作成
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # データベースをアプリケーションに初期化
    db.init_app(app)

    return app


def run_migration() -> None:
    """マイグレーションを実行する"""
    app = create_app_for_migration()

    print(f"マイグレーションを開始します: {DB_PATH}")

    with app.app_context():
        # テーブルが既に存在するか確認
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if "todos" in existing_tables:
            print("todosテーブルは既に存在します。マイグレーションをスキップします。")
            return

        # モデルからテーブルを作成
        db.create_all()
        print("todosテーブルが正常に作成されました。")

        #  (オプション)サンプルデータの挿入
        create_sample_data()


def create_sample_data() -> None:
    """サンプルデータを作成する (オプション)"""
    from datetime import date, timedelta, timezone

    jst = timezone(timedelta(hours=9))

    sample_todos = [
        Todo(
            title="プロジェクト計画書の作成",
            description="新規プロジェクトの計画書を作成する",
            due_date=date.today() + timedelta(days=7),
            priority="high",
            status="not_started",
        ),
        Todo(
            title="週次ミーティング",
            description="チームメンバーとの週次進捗確認",
            due_date=date.today() + timedelta(days=2),
            priority="medium",
            status="in_progress",
        ),
        Todo(
            title="ブログ記事の執筆",
            description="新機能についてのブログ記事を書く",
            due_date=date.today() + timedelta(days=14),
            priority="low",
            status="not_started",
        ),
    ]

    db.session.add_all(sample_todos)
    db.session.commit()
    print(f"{len(sample_todos)}件のサンプルデータを挿入しました。")


if __name__ == "__main__":
    run_migration()
    print("マイグレーションが完了しました。")
