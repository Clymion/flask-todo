"""ユーザーモデルを定義するモジュール"""

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

if TYPE_CHECKING:
    from api.models.todo import Todo
from api.utils.database import db

JST = ZoneInfo("Asia/Tokyo")


class User(db.Model):
    """
    ユーザーを表すモデルクラス

    SQLAlchemyを使用したORMマッピングを定義する
    """

    __tablename__ = "users"

    # 共有の時間生成関数
    @staticmethod
    def _get_jst_time() -> datetime:
        return datetime.now(tz=JST)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ToDoアイテムとの関連付け(1対多)
    todos: Mapped[list["Todo"]] = relationship(
        "Todo",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __init__(self, username: str, email: str, password: str) -> None:
        """
        ユーザーの初期化

        :param name: ユーザー名
        :param email: メールアドレス
        :param password: パスワード
        """
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.created_at = self._get_jst_time()

    def check_password(self, password: str) -> bool:
        """
        パスワードの検証

        :param password: 入力されたパスワード
        :return: パスワードが一致する場合はTrue、そうでない場合はFalse
        """
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        """モデルの文字列表現を定義"""
        return f"<User {self.id}: {self.username}>"
