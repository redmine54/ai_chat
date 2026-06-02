# 1. Python 3.12 の軽量公式イメージをベースにする
FROM python:3.12-slim

# 2. コンテナ内の作業ディレクトリを /app に設定
WORKDIR /app

# 3. コンテナの起動に必要なシステムパッケージ（Cコンパイラなど）を最小限インストール
# ※依存ライブラリ（chromadbクライアントなど）のビルドでエラーが出るのを防ぐため
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. パッケージ依存リスト（requirements.txt）をコンテナにコピー
COPY requirements.txt .

# 5. ライブラリをコンテナ環境へインストール
RUN pip install --no-cache-dir -r requirements.txt

# 6. バックエンドのソースコード（./src/backend の中身すべて）をコンテナにコピー
COPY . .

# 7. docker-compose.yml で指定されているポート 8000 を開放
EXPOSE 8000

# 8. バックエンドサーバーを起動するコマンド
# (ここでは FastAPI や LangChain 等でよく使われる uvicorn を想定しています)
# appフォルダの中のmain.pyを読み込むように指定
# (FastAPI + uvicorn の場合)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
