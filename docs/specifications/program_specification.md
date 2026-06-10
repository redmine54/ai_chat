# Program Specification
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-08</div>

対象モジュール名: ai_chat Backend（FastAPI）
作成者: 開発チーム
更新履歴:
- 2026-06-05 初版作成
- 2026-06-08 PDFインデクサー機能追加・Gemini API対応

---

## 1. 目的（Purpose）

本ドキュメントは、ai_chatバックエンドの処理仕様を定義し、開発・テスト・保守における共通理解を形成することを目的とする。

---

## 2. 前提条件（Prerequisites）

- 対象システム: ai_chat
- 使用技術: Python 3.12, FastAPI, ChromaDB（API v2）, Istio mTLS, Google Gemini API
- 実行環境: docker compose / Minikube / AKS
- 想定ユーザー: 社内従業員・管理者

---

## 3. 関連ドキュメント（Related Documents）

- System Overview
- API Specification
- Data Flow
- Error Handling
- Batch Specification

---

## 4. 処理概要（Process Overview）

### 4.1 チャット処理
1. ユーザーからの質問を受信（POST /api/chat）
2. Gemini gemini-embedding-2でクエリをベクトル化してChromaDBで類似検索
3. Gemini gemini-2.0-flashで回答を生成・返却

### 4.2 PDFインデックス化処理
1. data/配下のPDFファイル一覧を取得（GET /api/pdf/list）
2. 指定PDFをテキスト抽出・チャンク分割・Gemini gemini-embedding-2でベクトル化してChromaDBに登録（POST /api/pdf/index）

---

## 5. 環境変数（Environment Variables）

| 変数名 | 必須 | デフォルト値 | 説明 |
|--------|------|------------|------|
| GEMINI_API_KEY | ✅ | なし | Google Gemini API認証キー |
| CHROMA_HOST | ✅ | vectordb | ChromaDB接続ホスト名 |
| CHROMA_PORT | ✅ | 8000 | ChromaDB接続ポート |

> ⚠️ `GEMINI_API_KEY` はソースコードに直接記載禁止。`.env` ファイルまたはk8s Secretで管理すること。

---

## 6. 使用モデル（Models）

| 用途 | モデル名 | 説明 |
|------|---------|------|
| ベクトル化（埋め込み） | gemini-embedding-2 | PDFチャンク・クエリのベクトル化 |
| 回答生成 | gemini-2.0-flash | RAGコンテキストを元に回答生成 |

---

## 7. 入出力仕様（I/O Specification）

### 7.1 チャット機能

**入力（Input）:**

| 項目名 | 型 | 必須 | 説明 |
|--------|-----|------|------|
| message | string | ✅ | ユーザーの質問テキスト |

**出力（Output）:**

| 項目名 | 型 | 説明 |
|--------|-----|------|
| answer | string | Geminiが生成した回答テキスト |

### 7.2 PDFインデックス化機能

**入力（Input）:**

| 項目名 | 型 | 必須 | 説明 |
|--------|-----|------|------|
| filename | string | ✅ | data/配下のPDFファイル名 |

**出力（Output）:**

| 項目名 | 型 | 説明 |
|--------|-----|------|
| status | string | 処理結果（success / error） |
| filename | string | 処理したPDFファイル名 |
| document_id | string | ChromaDBに登録したドキュメントID |
| chunks | int | 登録したチャンク数 |

---

## 8. 詳細処理仕様（Detailed Logic）

### 8.1 チャット処理ステップ

| Step | 処理内容 | 条件 | 備考 |
|------|-----------|--------|--------|
| 1 | リクエスト受信 | POST /api/chat | Pydanticでバリデーション |
| 2 | クエリのベクトル化 | 常時 | Gemini gemini-embedding-2使用 |
| 3 | ChromaDB検索 | 常時 | TOP_K=5、コサイン類似度 |
| 4 | プロンプト生成 | 常時 | コンテキスト+質問を結合 |
| 5 | Gemini API呼び出し | 常時 | gemini-2.0-flash |
| 6 | レスポンス返却 | 常時 | 回答テキスト |

### 8.2 PDFインデックス化処理ステップ

| Step | 処理内容 | 条件 | 備考 |
|------|-----------|--------|--------|
| 1 | ファイル存在チェック | POST /api/pdf/index | 存在しない場合404を返却 |
| 2 | 拡張子チェック | 常時 | PDF以外は400を返却 |
| 3 | テキスト抽出 | 常時 | PyPDFを使用 |
| 4 | チャンク分割 | 常時 | chunk_size=500, overlap=100 |
| 5 | Geminiでベクトル化・ChromaDB登録 | 常時 | gemini-embedding-2使用 |
| 6 | チャンク数を返却 | 常時 | 登録件数を返却 |

### 8.3 擬似コード（Pseudo Code）

```python
# チャット処理
@app.post("/api/chat")
async def chat(request: ChatRequest):
    results = collection.query(query_texts=[request.message], n_results=5)
    context = "\n".join(results["documents"][0])
    prompt = f"【参考資料】\n{context}\n\n【質問】\n{request.message}"
    response = generation_model.generate_content(prompt)
    return {"answer": response.text}

# PDFインデックス化処理
@app.post("/api/pdf/index")
async def index_pdf(request: IndexRequest):
    pdf_path = os.path.join(DATA_DIR, request.filename)
    if not os.path.exists(pdf_path): raise HTTPException(404)
    if not request.filename.endswith(".pdf"): raise HTTPException(400)
    document_id = Path(request.filename).stem
    chunk_count = extract_and_store_pdf(pdf_path, document_id)
    return {"status": "success", "chunks": chunk_count}
```

---

## 9. エラー処理（Error Handling）

| エラーコード | 発生条件 | 対応 |
|--------------|------------|--------|
| E001 | ChromaDB接続失敗 | リトライ3回後エラー返却 |
| E002 | Gemini API失敗 | エラーメッセージ返却 |
| E003 | PDFパースエラー | スキップしてログに記録 |
| E004 | ベクトル化エラー（Gemini） | エラーメッセージ返却 |
| E005 | 関連ドキュメントなし | 専用メッセージ返却 |

---

## 10. 性能要件（Performance Requirements）

- チャット応答時間: 30秒以内
- ドキュメント検索時間: 3秒以内
- PDFインデックス化時間: ファイルサイズに依存（目安: 10MB以内で60秒以内）
- 同時接続ユーザー数: 10ユーザー以上
