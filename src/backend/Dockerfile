# 1. Python 3.12 の軽量公式イメージをベースにする
FROM python:3.12-slim

# 2. コンテナ内の作業ディレクトリを /app に設定
WORKDIR /app

# 3. システムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txtをコピー（コンテキストがルートのためパス変更）
COPY src/backend/requirements.txt .

# 5. ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 6. バックエンドのソースコードをコピー
COPY src/backend/ .

# 7. testsをコピー（Minikube・AKS・CI用）
COPY tests/ /app/tests/

# 8. docsをコピー（Minikube・AKS用）
COPY docs/ /app/docs/

# 9. README.mdをコピー
COPY README.md /app/README.md

# 10. ポート開放
EXPOSE 8000

# 11. サーバー起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
