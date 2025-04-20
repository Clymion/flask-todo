FROM python:3.11-bullseye

# gitとRedisサーバーのインストール
RUN apt-get update && \
    apt-get install -y git redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# llコマンドのエイリアスを追加
RUN echo "alias ll='ls -la'\n" >> ~/.bashrc

WORKDIR /workspaces

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 起動スクリプト
RUN chmod +x entrypoint.sh

# Flaskアプリが使用するポートを公開
EXPOSE 5000
# Redisが使用するポートを公開
EXPOSE 6379

# 開発サーバー起動コマンド
CMD ["./entrypoint.sh"]
