"""
エラーハンドリングに関する共通ユーティリティモジュール

API全体で一貫したエラーレスポンスを返すための関数群
"""

import json
from sqlite3 import Error as SQLiteError
from typing import Any, Dict, Optional, Tuple

from flask import Response, jsonify, request
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


def error_response(
    code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    error_type: Optional[str] = None,
) -> Tuple[Response, int]:
    """
    標準化されたエラーレスポンスを生成する

    Args:
        code: HTTPステータスコード
        message: エラーメッセージ
        details: 追加のエラー詳細情報 (オプション)
        error_type: エラータイプの識別子 (オプション)

    Returns:
        標準化されたJSONレスポンスとステータスコード

    """
    response_data = {"code": code, "message": message}

    if details:
        response_data["errors"] = details

    if error_type:
        response_data["error_type"] = error_type

    return jsonify(response_data), code


def validation_error(errors: Dict[str, str]) -> Tuple[Response, int]:
    """
    バリデーションエラーレスポンスを生成する

    Args:
        errors: フィールド名をキー、エラーメッセージを値とするディクショナリ

    Returns:
        標準化されたバリデーションエラーレスポンス

    """
    return error_response(400, "バリデーションエラー", errors)


def register_error_handlers(app):
    """
    アプリケーションにエラーハンドラを登録する

    Args:
        app: Flaskアプリケーションインスタンス

    """

    @app.errorhandler(400)
    def bad_request(e):
        return error_response(400, str(e) or "無効なリクエスト")

    @app.errorhandler(404)
    def not_found(e):
        return error_response(404, str(e) or "リソースが見つかりません")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response(405, f"メソッド {request.method} は許可されていません")

    @app.errorhandler(409)
    def conflict(e):
        return error_response(409, str(e) or "リソースの競合が発生しました")

    @app.errorhandler(500)
    def internal_server_error(e):
        return error_response(500, str(e) or "サーバー内部でエラーが発生しました")

    @app.errorhandler(SQLiteError)
    def handle_sqlite_error(e):
        return error_response(
            500,
            "データベースエラーが発生しました",
            error_type=e.__class__.__name__,
        )

    @app.errorhandler(json.JSONDecodeError)
    def handle_json_error(e):
        return error_response(400, f"JSONデコードエラー: {e!s}")

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        # marshmallowのValidationErrorはmessagesプロパティにエラー情報を持っている
        return validation_error(e.messages)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return error_response(e.code, e.description or str(e))

    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return error_response(401, str(e) or "認証エラー")

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # 本番環境では詳細なエラーメッセージを出力しないほうが良いことに注意
        app.logger.error(f"予期しないエラー: {str(e)}")
        return error_response(500, "予期しないエラーが発生しました")
