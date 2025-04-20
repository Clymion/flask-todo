""".env file validator"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数の設定を管理するクラス"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    JWT_SECRET_KEY: SecretStr = Field(
        min_length=32,
        description="JWTの秘密鍵(32文字以上推奨)",
    )
    # JWTの有効期限(秒): 最大1日間
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        default=3600,
        ge=1,
        le=60 * 60 * 24,
        description="JWTの有効期限(秒)",
    )
    # JWTのリフレッシュトークンの有効期限(秒): 最大30日間
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(
        default=60 * 60 * 24 * 30,
        ge=1,
        le=60 * 60 * 24 * 30,  # 30日間
        description="JWTのリフレッシュトークンの有効期限(秒)",
    )

    # Redisの設定
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redisのホスト名",
    )
    REDIS_PORT: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redisのポート番号",
    )
    REDIS_DB: int = Field(
        default=0,
        ge=0,
        le=15,
        description="RedisのDB番号",
    )
    REDIS_PASSWORD: str = Field(
        default="",
        description="Redisのパスワード",
    )


# インスタンス化して使う(遅延ロードされます)  # noqa: ERA001
settings = Settings()
