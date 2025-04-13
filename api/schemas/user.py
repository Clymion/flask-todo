"""
ToDoアイテムのバリデーションと変換を行うスキーマ定義
"""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from flask_marshmallow import Marshmallow
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_dump,
    validate,
    validates,
    validates_schema,
)


class UserSchema(Schema):
    """ユーザーのメインスキーマ"""

    id = fields.Integer(dump_only=True, load_default=None)
    username = fields.String(
        required=True,
        validate=validate.Length(
            min=3,
            max=50,
            error="ユーザー名は3〜50文字である必要があります",
        ),
    )
    email = fields.Email(required=True)
    password = fields.String(
        load_only=True,
        required=True,
        validate=validate.Length(
            min=8,
            max=200,
            error="パスワードは8〜200文字である必要があります",
        ),
    )
    created_at = fields.NaiveDateTime(
        timezone=ZoneInfo("Asia/Tokyo"),
        dump_only=True,
        format="iso",
    )

    @post_dump
    def set_timezone(self, data: dict, **kwargs) -> dict:
        """
        タイムゾーンを設定する

        data["created_at"]とdata["updated_at"]は既にisoformatの`str`型であるため、
        一度datetimeに変換してtzinfoを設定してから、再度isoformatに変換する
        """
        if "created_at" in data:
            created_at_obj = datetime.fromisoformat(data["created_at"])
            data["created_at"] = created_at_obj.replace(
                tzinfo=ZoneInfo("Asia/Tokyo"),
            ).isoformat()
        return data


class AtLeastOneOfUsernameOrEmail:
    """ユーザー名またはメールアドレスのいずれかが必要なバリデーション"""

    @validates_schema
    def validate_username_or_email(self, data: dict, **kwargs) -> None:
        """
        ユーザー名またはメールアドレスのいずれかが必要なバリデーション

        :param data: 入力データ
        :raises ValidationError: ユーザー名とメールアドレスの両方が不正な場合
        """
        if not (data.get("username") or data.get("email")):
            msg = "ユーザー名またはメールアドレスのいずれかを指定してください"
            raise ValidationError(msg, field_name=["username", "email"])


class UserRegisterSchema(UserSchema, AtLeastOneOfUsernameOrEmail):
    """ユーザー登録用のスキーマ"""

    @validates("username")
    def validate_username(self, username: str) -> None:
        """
        ユーザー名のバリデーション

        :param username: ユーザー名
        :raises ValidationError: ユーザー名が不正な場合
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            msg = "ユーザー名は英数字とアンダースコア(_)のみを使用できます"
            raise ValidationError(msg)

    @validates("password")
    def validate_password(self, password: str) -> None:
        """
        パスワードのバリデーション

        :param password: パスワード
        :raises ValidationError: パスワードが不正な場合
        """
        # 記号も許容するが、必須ではない
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+=-]+$", password):
            msg = "パスワードは8文字以上で、英字と数字を含む必要があります"
            raise ValidationError(msg)

    class Meta:
        """スキーマのメタ情報"""

        unknown = "exclude"


class UserLoginSchema(Schema, AtLeastOneOfUsernameOrEmail):
    """
    ユーザーログイン用のスキーマ

    ユーザ名またはメールアドレスとパスワードを使用してログインするためのスキーマ
    """

    password = Marshmallow().auto_field(load_only=True)

    class Meta:
        """スキーマのメタ情報"""

        unknown = "exclude"
