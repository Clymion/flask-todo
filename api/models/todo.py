"""
Todoモデル定義

- id: 一意の識別子（整数・主キー）
- title: タイトル（文字列・必須・最大100文字）
- description: 説明（文字列・任意・最大500文字）
- due_date: 期限日（日付・任意・YYYY-MM-DD形式）
- priority: 優先度（low/medium/high・デフォルトはmedium）
- status: 状態（not_started/in_progress/completed・デフォルトはnot_started）
- created_at: 作成日時（自動生成）
- updated_at: 更新日時（自動更新）
"""

from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Enum("low", "medium", "high"), default="medium")
    status = db.Column(
        db.Enum("not_started", "in_progress", "completed"), default="not_started"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Todo {self.title}>"
