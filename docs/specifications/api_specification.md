# API Specification
<div align="right">作成日: 2026-06-05</div>

API名: ai_chat Backend API
作成者: 開発チーム
更新履歴: 2026-06-05 初版作成

---

## 1. 概要（Overview）

ai_chatバックエンドのREST API仕様を定義する。FastAPIで実装されており、Swagger UIは`/docs`で参照可能。

---

## 2. エンドポイント一覧（Endpoint List）

| No | API名 | Method | Path | 説明 |
|----|-------|--------|------|------|
| 1 | チャット | POST | /api/chat | 質問を送信して回答を取得 |
| 2 | ヘルスチェック | GET | /health | システム稼働状態確認 |
| 3 | ドキュメントビューア | GET | /specs | プロジェクトドキュメント表示 |
| 4 | APIドキュメント | GET | /docs | Swagger UI |

---

## 3. 認証方式（Authentication）

- 現状: 認証なし（開発フェーズ）
- 予定: Azure AD連携（Bearer Token）

---

## 4. エンドポイント詳細

### 4.1 POST /api/chat

**概要:** ユーザーの質問を受け取り、RAG+LLMで回答を生成して返却する。

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

## 5. ステータスコード（Status Codes）

| コード | 説明 |
|--------|------|
| 200 | 正常 |
| 400 | 不正リクエスト |
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

### レスポンス

```json
{
  "answer": "社内規程については、第1条に..."
}
```
