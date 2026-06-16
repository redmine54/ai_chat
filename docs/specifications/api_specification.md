# API Specification
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-14</div>

API名: ai_chat Backend API
作成者: 開発チーム
更新履歴:
- 2026-06-05 初版作成
- 2026-06-08 PDFインデクサーAPI追加・Gemini API対応
- 2026-06-14 /health追加・/api/pdf/status・/api/pdf/delete追加

---

## 1. 概要（Overview）

ai_chatバックエンドのREST API仕様を定義する。FastAPIで実装されており、Swagger UIは`/swagger/docs`で参照可能。LLMはGoogle Gemini API（gemini-2.0-flash）、埋め込みモデルはgemini-embedding-2を使用する。

---

## 2. エンドポイント一覧（Endpoint List）

| No | API名 | Method | Path | 説明 |
|----|-------|--------|------|------|
| 1 | ヘルスチェック | GET | /health | システム稼働状態確認 |
| 2 | チャット | POST | /api/chat | 質問を送信してGemini RAGで回答を取得 |
| 3 | PDFファイル一覧 | GET | /api/pdf/list | data/配下のPDFファイル一覧取得 |
| 4 | PDFインデックス化 | POST | /api/pdf/index | 指定PDFをChromaDBにインデックス化 |
| 5 | PDFステータス確認 | GET | /api/pdf/status | PDFの登録状況・ページ数・チャンク数確認 |
| 6 | PDFデータ削除 | DELETE | /api/pdf/delete | ChromaDBから指定ドキュメントを削除 |
| 7 | ドキュメントビューア | GET | /api/specs | プロジェクトドキュメント表示 |
| 8 | APIドキュメント | GET | /swagger/docs | Swagger UI |
| 9 | PDFインデクサー画面 | GET | /api/indexer | PDFインデクサーWebUI表示 |
| 10 | チャット画面 | GET | / または /api/chat/ui | チャットWebUI表示 |

---

## 3. 認証方式（Authentication）

- 現状: 認証なし（開発フェーズ）
- 予定: Azure AD連携（Bearer Token）

---

## 4. エンドポイント詳細

### 4.1 GET /health

**概要:** システムの稼働状態を確認する。

**成功レスポンス（200 OK）:**
```json
{
  "status": "ok"
}
```

---

### 4.2 POST /api/chat

**概要:** ユーザーの質問を受け取り、Gemini gemini-embedding-2でベクトル検索しgemini-2.0-flashで回答を生成して返却する。回答はMarkdown形式。

**Request Body:**
```json
{
  "message": "社内規程について教えてください",
  "model": "models/gemini-2.5-flash"
}
```

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| message | string | ✅ | - | ユーザーの質問テキスト |
| model | string | ❌ | models/gemini-2.5-flash | 使用するGeminiモデル |

**成功レスポンス（200 OK）:**
```json
{
  "answer": "社内規程については..."
}
```

**エラーレスポンス（422）:**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 4.3 GET /api/pdf/list

**概要:** `src/backend/data/` 配下のPDFファイル一覧を返す。

**成功レスポンス（200 OK）:**
```json
{
  "files": [
    "業務委託契約書260601-0630.pdf",
    "社内規程.pdf"
  ]
}
```

---

### 4.4 POST /api/pdf/index

**概要:** 指定したPDFファイルをテキスト抽出・チャンク分割・Gemini gemini-embedding-2でベクトル化してChromaDBに登録する。

**Request Body:**
```json
{
  "filename": "業務委託契約書260601-0630.pdf",
  "force": false
}
```

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| filename | string | ✅ | - | data/配下のPDFファイル名 |
| force | boolean | ❌ | false | 強制再登録フラグ |

**成功レスポンス（200 OK）:**
```json
{
  "status": "success",
  "filename": "業務委託契約書260601-0630.pdf",
  "document_id": "業務委託契約書260601-0630",
  "chunks": 12
}
```

**エラーレスポンス（404）:**
```json
{
  "detail": "ファイルが見つかりません: xxx.pdf"
}
```

**エラーレスポンス（400）:**
```json
{
  "detail": "PDFファイルのみ対応しています"
}
```

---

### 4.5 GET /api/pdf/status

**概要:** 指定PDFの登録状況・ページ数・チャンク数を返す。

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| filename | string | ✅ | 確認するPDFファイル名 |

**成功レスポンス（200 OK）:**
```json
{
  "filename": "業務委託契約書260601-0630.pdf",
  "document_id": "業務委託契約書260601-0630",
  "page_count": 5,
  "chunk_count": 12,
  "status": "registered",
  "pdf_mtime": 1234567890.0,
  "registered_at": 1234567890.0
}
```

**statusの値:**

| 値 | 説明 |
|----|------|
| registered | 登録済み（最新） |
| outdated | 登録済みだがPDFが更新されている |
| unregistered | 未登録 |

---

### 4.6 DELETE /api/pdf/delete

**概要:** ChromaDBから指定ドキュメントのデータを削除する。

**Request Body:**
```json
{
  "document_id": "業務委託契約書260601-0630"
}
```

**成功レスポンス（200 OK）:**
```json
{
  "status": "success",
  "document_id": "業務委託契約書260601-0630",
  "deleted_chunks": 12
}
```

**エラーレスポンス（404）:**
```json
{
  "detail": "登録データが見つかりません: 業務委託契約書260601-0630"
}
```

---

## 5. ステータスコード（Status Codes）

| コード | 説明 |
|--------|------|
| 200 | 正常 |
| 400 | 不正リクエスト（PDF以外のファイル等） |
| 404 | リソースが見つからない（ファイル未存在等） |
| 422 | バリデーションエラー |
| 500 | サーバーエラー |
| 503 | サービス利用不可 |

---

## 6. 性能要件（Performance Requirements）

- タイムアウト: 30秒
- 最大リクエストサイズ: 10MB

---

## 7. サンプル（Examples）

```bash
# ヘルスチェック
curl http://localhost:8000/health

# チャットAPIの呼び出し
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "社内規程について教えてください"}'

# PDFファイル一覧の取得
curl "http://localhost:8000/api/pdf/list"

# PDFのインデックス化
curl -X POST "http://localhost:8000/api/pdf/index" \
  -H "Content-Type: application/json" \
  -d '{"filename": "業務委託契約書260601-0630.pdf"}'

# PDFのステータス確認
curl "http://localhost:8000/api/pdf/status?filename=業務委託契約書260601-0630.pdf"

# PDFデータの削除
curl -X DELETE "http://localhost:8000/api/pdf/delete" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "業務委託契約書260601-0630"}'
```
