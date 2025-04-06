"""
Todoモデル定義

- id: 一意の識別子 (整数・主キー)
- title: タイトル (文字列・必須・最大100文字)
- description: 説明 (文字列・任意・最大500文字)
- due_date: 期限日 (日付・任意・YYYY-MM-DD形式)
- priority: 優先度 (low/medium/high・デフォルトはmedium)
- status: 状態 (not_started/in_progress/completed・デフォルトはnot_started)
- created_at: 作成日時 (自動生成)
- updated_at: 更新日時 (自動更新)
"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.utils.database import db


class Todo(db.Model):
    """ToDoアイテムのデータベースモデル"""

    __tablename__ = "todos"

    # 共有の時間生成関数
    @staticmethod
    def _get_jst_time() -> datetime:
        return datetime.now(timezone(timedelta(hours=9)))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", name="priority_enum"),
        default="medium",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("not_started", "in_progress", "completed", name="status_enum"),
        default="not_started",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_get_jst_time,  # staticmethodを参照
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_get_jst_time,  # 同じstaticmethodを参照
        onupdate=lambda: datetime.now(
            timezone(timedelta(hours=9)),
        ),  # 更新時は新しい時間
        nullable=False,
    )

    def __init__(self, **kwargs) -> None:
        """コンストラクタで初期値を設定"""
        now = datetime.now(timezone(timedelta(hours=9)))
        kwargs["created_at"] = now
        kwargs["updated_at"] = now
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """
        モデルの文字列表現を定義"""
        return f"<Todo {self.title}>"

    def to_dict(self):
        """モデルを辞書形式に変換"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
