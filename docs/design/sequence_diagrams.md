# Sequence Diagrams
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-14</div>

## シーケンス図

### SD-001: チャット処理フロー

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant UI as チャット画面\n/
    participant BE as Backend\nFastAPI
    participant DB as ChromaDB
    participant LLM as Gemini API\ngemini-2.5-flash

    User->>UI: 質問入力・送信
    UI->>BE: POST /api/chat\n{message: "..."}
    BE->>BE: gemini-embedding-2で\nクエリをベクトル化
    BE->>DB: query_embeddings\nn_results=5
    DB-->>BE: 関連ドキュメント（TOP5）
    BE->>LLM: プロンプト生成・送信\n（参考資料+質問）
    LLM-->>BE: 回答生成（Markdown形式）
    BE-->>UI: {"answer": "..."}
    UI-->>User: AIバブルでMarkdownレンダリング表示
```

---

### SD-002: PDFインデックス化フロー

```mermaid
sequenceDiagram
    actor Admin as 管理者
    participant UI as インデクサーWebUI\n/api/indexer
    participant BE as Backend
    participant Gemini as Gemini API\ngemini-embedding-2
    participant DB as ChromaDB

    Admin->>UI: ブラウザでアクセス
    UI->>BE: GET /api/pdf/list
    BE-->>UI: PDFファイル一覧
    UI-->>Admin: ファイル一覧表示（登録状況付き）

    Admin->>UI: インデックス化ボタンをクリック
    UI->>BE: POST /api/pdf/index\n{filename: "xxx.pdf"}
    BE->>BE: ファイル存在チェック
    BE->>BE: テキスト抽出（PyPDF）
    BE->>BE: チャンク分割（500文字）
    loop チャンクごと
        BE->>Gemini: embed_content\ntask_type=retrieval_document
        Gemini-->>BE: embedding vector
    end
    BE->>DB: collection.add\n(documents, embeddings, ids)
    DB-->>BE: 保存完了
    BE-->>UI: {status: success, chunks: N}
    UI-->>Admin: 完了ログ表示
```

---

### SD-003: ヘルスチェックフロー

```mermaid
sequenceDiagram
    participant MON as 監視システム
    participant BE as Backend
    participant DB as ChromaDB

    MON->>BE: GET /health
    BE-->>MON: {"status": "ok"}
```

---

### SD-004: mTLS通信フロー

```mermaid
sequenceDiagram
    participant BE as Backend\n(Envoy Sidecar)
    participant DB as ChromaDB\n(Envoy Sidecar)

    BE->>DB: TLS ClientHello
    DB-->>BE: TLS ServerHello
    BE->>DB: クライアント証明書（SPIFFE）
    DB-->>BE: サーバー証明書（SPIFFE）
    BE->>DB: 証明書検証（STRICT）
    DB-->>BE: 証明書検証（STRICT）
    BE->>DB: 暗号化通信開始
```

---

### SD-005: CI/CDフロー

```mermaid
sequenceDiagram
    actor Dev as 開発者
    participant GH as GitHub
    participant Runner as Self-hosted Runner\n(Mac M1)
    participant Docker as Docker
    participant Trivy as Trivy

    Dev->>GH: Push（feature/**）
    GH->>Runner: Job実行
    Runner->>Docker: build（ai_chat-backend:latest）
    Runner->>Docker: ruff format / ruff check / mypy
    Runner->>Docker: pytest tests/unit/ --cov
    Runner->>Docker: pytest tests/integration/
    Runner->>Trivy: image scan（.trivyignore適用）
    Trivy-->>Runner: 脆弱性レポート
    Runner-->>GH: CI結果通知
    Dev->>GH: Pull Request → main
    Dev->>GH: workflow_dispatch: cd_only
    GH->>Runner: デプロイジョブ実行
    Runner->>Docker: docker compose up -d
    Docker-->>Runner: 起動完了
    Runner-->>GH: デプロイ完了
```

---

### SD-006: ngrok外部公開フロー（ユーザーレビュー用）

```mermaid
sequenceDiagram
    actor Admin as 管理者
    participant ngrok as ngrok
    participant FE as Frontend\nNginx:80
    participant BE as Backend\nFastAPI:8000
    actor User as 外部ユーザー

    Admin->>ngrok: ngrok http 80
    ngrok-->>Admin: https://xxxx.ngrok-free.dev
    Admin->>User: URLを共有

    User->>ngrok: https://xxxx.ngrok-free.dev
    ngrok->>FE: http://localhost:80
    FE->>BE: proxy_pass /api/
    BE-->>FE: レスポンス
    FE-->>ngrok: レスポンス
    ngrok-->>User: チャット画面表示
```
