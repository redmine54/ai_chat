# Program Specification
<div align="right">作成日: 2026-06-05</div>

対象モジュール名: ai_chat Backend（FastAPI）
作成者: 開発チーム
更新履歴: 2026-06-05 初版作成

---

## 1. 目的（Purpose）

本ドキュメントは、ai_chatバックエンドの処理仕様を定義し、開発・テスト・保守における共通理解を形成することを目的とする。

---

## 2. 前提条件（Prerequisites）

- 対象システム: ai_chat
- 使用技術: Python 3.12, FastAPI, ChromaDB（API v2）, Istio mTLS
- 実行環境: docker compose / Minikube / AKS
- 想定ユーザー: 社内従業員

---

## 3. 関連ドキュメント（Related Documents）

- System Overview
- API Specification
- Data Flow
- Error Handling

---

## 4. 処理概要（Process Overview）

1. ユーザーからの質問を受信（POST /api/chat）
2. 質問をベクトル化してChromaDBで類似検索
3. LLMに送信して回答を生成・返却

---

## 5. 入出力仕様（I/O Specification）

### 5.1 入力（Input）

| 項目名 | 型 | 必須 | 説明 |
|--------|-----|------|------|
| message | string | ✅ | ユーザーの質問テキスト |

### 5.2 出力（Output）

| 項目名 | 型 | 説明 |
|--------|-----|------|
| answer | string | LLMが生成した回答テキスト |

---

## 6. 詳細処理仕様（Detailed Logic）

### 6.1 処理ステップ

| Step | 処理内容 | 条件 | 備考 |
|------|-----------|--------|--------|
| 1 | リクエスト受信 | POST /api/chat | Pydanticでバリデーション |
| 2 | 質問のベクトル化 | 常時 | Embedding Model使用 |
| 3 | ChromaDB検索 | 常時 | TOP_K=5、コサイン類似度 |
| 4 | プロンプト生成 | 常時 | システムプロンプト+コンテキスト+質問 |
| 5 | LLM API呼び出し | 常時 | タイムアウト設定あり |
| 6 | レスポンス返却 | 常時 | 回答テキスト+参照ドキュメント |

### 6.2 擬似コード（Pseudo Code）

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 1. 質問のベクトル化
    vector = embedding_model.encode(request.message)
    
    # 2. ChromaDB検索（API v2）
    results = chroma_client.query(
        query_embeddings=[vector],
        n_results=TOP_K
    )
    
    # 3. プロンプト生成
    context = "\n".join(results["documents"])
    prompt = f"{SYSTEM_PROMPT}\n\nコンテキスト:\n{context}\n\n質問: {request.message}"
    
    # 4. LLM API呼び出し
    answer = llm_client.generate(prompt)
    
    return {"answer": answer}
```

---

## 7. エラー処理（Error Handling）

| エラーコード | 発生条件 | 対応 |
|--------------|------------|--------|
| E001 | ChromaDB接続失敗 | リトライ3回後エラー返却 |
| E002 | LLM API失敗 | エラーメッセージ返却 |
| E005 | 関連ドキュメントなし | 専用メッセージ返却 |

---

## 8. 性能要件（Performance Requirements）

- チャット応答時間: 30秒以内
- ドキュメント検索時間: 3秒以内
- 同時接続ユーザー数: 10ユーザー以上
