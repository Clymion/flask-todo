"""
Userに関するビジネスロジックを実装するサービスモジュール
"""

from typing import Any, Optional

from werkzeug.exceptions import Conflict, NotFound

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
