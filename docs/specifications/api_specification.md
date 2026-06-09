# API Specification
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-08</div>

API名: ai_chat Backend API
作成者: 開発チーム
更新履歴:
- 2026-06-05 初版作成
- 2026-06-08 PDFインデクサーAPI追加・Gemini API対応

---

## 1. 概要（Overview）

ai_chatバックエンドのREST API仕様を定義する。FastAPIで実装されており、Swagger UIは`/swagger/docs`で参照可能。LLMはGoogle Gemini API（gemini-2.0-flash）、埋め込みモデルはgemini-embedding-2を使用する。

---

## 2. エンドポイント一覧（Endpoint List）

| No | API名 | Method | Path | 説明 |
|----|-------|--------|------|------|
| 1 | チャット | POST | /api/chat | 質問を送信してGemini RAGで回答を取得 |
| 2 | ヘルスチェック | GET | /health | システム稼働状態確認 |
| 3 | ドキュメントビューア | GET | /api/specs | プロジェクトドキュメント表示 |
| 4 | APIドキュメント | GET | /swagger/docs | Swagger UI |
| 5 | PDFファイル一覧 | GET | /api/pdf/list | data/配下のPDFファイル一覧取得 |
| 6 | PDFインデックス化 | POST | /api/pdf/index | 指定PDFをGemini gemini-embedding-2でChromaDBにインデックス化 |
| 7 | PDFインデクサー画面 | GET | /api/indexer | PDFインデクサーWebUI表示 |

---

## 3. 認証方式（Authentication）

- 現状: 認証なし（開発フェーズ）
- 予定: Azure AD連携（Bearer Token）

---

## 4. エンドポイント詳細

### 4.1 POST /api/chat

**概要:** ユーザーの質問を受け取り、Gemini gemini-embedding-2でベクトル検索しgemini-2.0-flashで回答を生成して返却する。

**Request Body:**
```json
{
  "message": "社内規程について教えてください"
}
```

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| message | string | ✅ | ユーザーの質問テキスト |

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

### 4.2 GET /health

**概要:** システムの稼働状態を確認する。

**成功レスポンス（200 OK）:**
```json
{
  "status": "ok"
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
  "filename": "業務委託契約書260601-0630.pdf"
}
```

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| filename | string | ✅ | data/配下のPDFファイル名 |

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

**エラーレスポンス（500）:**
```json
{
  "detail": "インデックス化に失敗しました: ..."
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

### チャットAPIの呼び出し

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "社内規程について教えてください"}'
```

### PDFファイル一覧の取得

```bash
curl "http://localhost:8000/api/pdf/list"
```

### PDFのインデックス化

```bash
curl -X POST "http://localhost:8000/api/pdf/index" \
  -H "Content-Type: application/json" \
  -d '{"filename": "業務委託契約書260601-0630.pdf"}'
```

### レスポンス

```json
{
  "status": "success",
  "filename": "業務委託契約書260601-0630.pdf",
  "document_id": "業務委託契約書260601-0630",
  "chunks": 12
}
```
