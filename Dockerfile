FROM python:3.11-slim

# gitのインストールと必要なツールのセットアップ
RUN apt-get update && \
    apt-get install -y git && \
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

# Flaskアプリが使用するポートを公開
EXPOSE 5000

# 開発サーバー起動コマンド
CMD ["flask", "--app", "api", "run", "--host=0.0.0.0"]
