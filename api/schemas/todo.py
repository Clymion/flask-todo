"""
ToDoアイテムのバリデーションと変換を行うスキーマ定義
"""

import re
from datetime import datetime

from marshmallow import Schema, ValidationError, fields, validate, validates


class TodoSchema(Schema):
    """ToDoアイテムのメインスキーマ"""

    # idフィールドを上書きして、リクエストに含まれていても無視される設定
    id = fields.Integer(dump_only=True, load_default=None)
    title = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            max=100,
            error="タイトルは1〜100文字である必要があります",
        ),
    )
    description = fields.String(
        validate=validate.Length(
            max=500,
            error="説明は500文字以内である必要があります",
        ),
        allow_none=True,
    )
    due_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    priority = fields.String(
        validate=validate.OneOf(
            ["low", "medium", "high"],
            error="優先度は次のいずれかである必要があります: low, medium, high",
        ),
        dump_default="medium",
    )
    status = fields.String(
        validate=validate.OneOf(
            ["not_started", "in_progress", "completed"],
            error="ステータスは次のいずれかである必要があります: not_started, in_progress, completed",
        ),
        dump_default="not_started",
    )
    created_at = fields.DateTime(dump_only=True)  # 読み取り専用
    updated_at = fields.DateTime(dump_only=True)  # 読み取り専用

    @validates("due_date")
    def validate_due_date(self, value: str) -> None:
        """日付形式の追加バリデーション"""
        if value is None:
            return

        if isinstance(value, str):
            # YYYY-MM-DD形式かどうかチェック
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if not date_pattern.match(value):
                msg = "無効な日付形式です。期待される形式: YYYY-MM-DD"
                raise ValidationError(msg)

            try:
                # 正しい日付かどうかチェック (例: 2023-02-31はエラー)
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                msg = "無効な日付です"
                raise ValidationError(msg)


class TodoCreateSchema(TodoSchema):
    """ToDo作成用スキーマ"""

    # 作成時は、基本スキーマを継承し、特別な処理が必要な場合はここに追加

    class Meta:
        """メタデータクラス"""

        # 未知のフィールドを除外
        unknown = "exclude"


class TodoUpdateSchema(TodoSchema):
    """ToDo更新用スキーマ"""

    # 更新時は、すべてのフィールドがオプション
    title = fields.String(
        validate=validate.Length(
            min=1,
            max=100,
            error="タイトルは1〜100文字である必要があります",
        ),
        required=False,
    )

    class Meta:
        """メタデータクラス"""

        # 未知のフィールドを除外
        unknown = "exclude"


class TodoQuerySchema(Schema):
    """ToDo一覧取得のクエリパラメータ用スキーマ"""

    id = fields.Integer(
        validate=validate.Range(
            min=1,
            error="IDは1以上の整数である必要があります",
        ),
        required=False,
        allow_none=True,
    )
    status = fields.String(
        validate=validate.OneOf(
            ["not_started", "in_progress", "completed"],
            error="ステータスは次のいずれかである必要があります: not_started, in_progress, completed",
        ),
        required=False,
        allow_none=True,
    )
    priority = fields.String(
        validate=validate.OneOf(
            ["low", "medium", "high"],
            error="優先度は次のいずれかである必要があります: low, medium, high",
        ),
        required=False,
        allow_none=True,
    )
    due_before = fields.Date(format="%Y-%m-%d", required=False, allow_none=True)
    due_after = fields.Date(format="%Y-%m-%d", required=False, allow_none=True)

    @validates("due_before")
    def validate_due_before(self, value: str) -> None:
        """日付形式の追加バリデーション"""
        self._validate_date_format(value, "due_before")

    @validates("due_after")
    def validate_due_after(self, value: str) -> None:
        """日付形式の追加バリデーション"""
        self._validate_date_format(value, "due_after")

    def _validate_date_format(self, value: str, field_name: str) -> None:
        """日付形式の共通バリデーション"""
        if value is None:
            return

        if isinstance(value, str):
            # YYYY-MM-DD形式かどうかチェック
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if not date_pattern.match(value):
                msg = "無効な日付形式です。期待される形式: YYYY-MM-DD"
                raise ValidationError(msg, field_name=field_name)

            try:
                # 正しい日付かどうかチェック(例: 2023-02-31はエラー)
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                msg = "無効な日付です"
                raise ValidationError(msg, field_name=field_name)


# スキーマのインスタンスを作成
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
todo_create_schema = TodoCreateSchema()
todo_update_schema = TodoUpdateSchema()
todo_query_schema = TodoQuerySchema()
