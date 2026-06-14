# 1. Python 3.12 の軽量公式イメージをベースにする
FROM python:3.12-slim

# 2. コンテナ内の作業ディレクトリを /app に設定
WORKDIR /app

# 3. システムパッケージのインストール（tesseract OCR追加）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-jpn \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ★ ここで API バージョンを v1 に固定（最重要）
ENV GOOGLE_API_VERSION=v1

# 4. google-generativeai を最新化
#RUN pip install --upgrade google-generativeai

# 5. requirements.txt をコピー
#COPY src/backend/requirements.txt .

# 6. ライブラリをインストール
#RUN pip install --no-cache-dir -r requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 7. バックエンドのソースコードをコピー
COPY src/backend/app /app
#COPY src/backend/ .

# 8. tests をコピー
COPY tests/ /app/tests/

# 9. docs をコピー
COPY docs/ /app/docs/

# 10. README.md をコピー
COPY README.md /app/README.md

# 11. ポート開放の前に追加
# 実行ユーザーをrootから変更（ホスト側のファイル権限問題を回避）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 12. ポート開放
EXPOSE 8000

# 13. サーバー起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
