"""
Userに関するビジネスロジックを実装するサービスモジュール
"""

from typing import Any, Optional

from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import Conflict

from api.models.user import User, db


class UserService:
    """
    User操作と関連するビジネスロジックを提供するサービスクラス
    """

    @staticmethod
    def register_user(user_data: dict[str, Any]) -> User:
        """
        新しいユーザーを登録する

        Args:
            user_data: ユーザー情報

        Returns:
            登録されたユーザー

        """
        # ユーザー名の重複チェック
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if existing_user:
            msg = "ユーザー名は既に使用されています"
            raise Conflict(msg)

        # メールアドレスの重複チェック
        existing_email = User.query.filter_by(email=user_data["email"]).first()
        if existing_email:
            msg = "メールアドレスは既に使用されています"
            raise Conflict(msg)

        # 新しいユーザーを作成
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

        return new_user

    @staticmethod
    def login_user(user_data: dict[str, Any]) -> Optional[User]:
        """
        ユーザーをログインさせる

        Args:
            user_data: ログイン情報

        Returns:
            ログインしたユーザー

        """
        # ユーザー名またはメールアドレスでユーザーを取得
        user: User | None = User.query.filter(
            (User.username == user_data["username"])
            | (User.email == user_data["username"]),
        ).first()

        if not user:
            msg = "ユーザー名またはパスワードが不正です"
            raise NoAuthorizationError(msg)

        # パスワードの確認
        if not user.check_password(user_data["password"]):
            msg = "ユーザー名またはパスワードが不正です"
            raise NoAuthorizationError(msg)

        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        ユーザーIDからユーザーを取得する

        Args:
            user_id: ユーザーID

        Returns:
            ユーザー情報

        """
        return User.query.get(user_id)
