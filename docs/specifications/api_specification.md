# API Specification
API 名：
作成日：
作成者：
更新履歴：

---

## 1. 概要（Overview）
本 API の機能、入出力仕様、エラー仕様、認証方式を定義する。

---

## 2. エンドポイント一覧（Endpoint List）
| No | API 名 | Method | Path | 説明 |
|----|--------|--------|------|------|

---

## 3. 認証方式（Authentication）
- 認証方式：Bearer Token / API Key / OAuth2
- 認可：RBAC

---

## 4. リクエスト仕様（Request Specification）

### 4.1 Path Parameters
| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|

### 4.2 Query Parameters
| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|

### 4.3 Request Body
\`\`\`
{
}
\`\`\`

---

## 5. レスポンス仕様（Response Specification）

### 5.1 成功レスポンス（200 OK）
\`\`\`
{
  "status": "success",
  "data": {}
}
\`\`\`

### 5.2 エラーレスポンス
\`\`\`
{
  "status": "error",
  "error_code": "",
  "message": ""
}
\`\`\`

---

## 6. ステータスコード（Status Codes）
| コード | 説明 |
|--------|------|
| 200 | 正常 |
| 400 | 不正リクエスト |
| 401 | 認証エラー |
| 403 | 権限エラー |
| 404 | 未検出 |
| 500 | サーバーエラー |

---

## 7. エラー仕様（Error Handling）
| エラーコード | HTTP | 説明 | 対応 |
|--------------|------|------|------|

---

## 8. 性能要件（Performance Requirements）
- タイムアウト：
- 最大リクエストサイズ：

---

## 9. セキュリティ要件（Security Requirements）
- 入力バリデーション：
- HTTPS 必須：

---

## 10. サンプル（Examples）
### Request
\`\`\`
curl -X GET "https://api.example.com/v1/resource" \
  -H "Authorization: Bearer {token}"
\`\`\`

### Response
\`\`\`
{
  "status": "success",
  "data": {}
}
\`\`\`

