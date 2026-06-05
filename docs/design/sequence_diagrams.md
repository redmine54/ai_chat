# Sequence Diagrams
<div align="right">作成日: 2026-06-05</div>

## シーケンス図

### SD-001: チャット処理フロー

```
ユーザー    Frontend    Backend    ChromaDB    LLM
   │           │           │           │        │
   │─ 質問入力 ─▶│           │           │        │
   │           │─ POST /api/chat ─▶│    │        │
   │           │           │─ ベクトル化 ─▶│       │
   │           │           │           │        │
   │           │           │─ 類似検索 ──▶│       │
   │           │           │◀─ 関連ドキュメント ─│  │
   │           │           │                    │
   │           │           │─ プロンプト生成 ────▶│
   │           │           │◀─ 回答生成 ──────────│
   │           │           │                    │
   │           │◀─ 回答 ────│           │        │
   │◀─ 回答表示 ─│           │           │        │
```

---

### SD-002: PDFアップロードフロー

```
管理者      Frontend    Backend    ChromaDB
   │           │           │           │
   │─ PDF選択 ─▶│           │           │
   │           │─ POST /api/docs ─▶│    │
   │           │           │─ テキスト抽出        │
   │           │           │─ チャンク分割        │
   │           │           │─ ベクトル化          │
   │           │           │─ 保存（/api/v2） ───▶│
   │           │           │◀─ 保存完了 ──────────│
   │           │◀─ 完了 ────│           │
   │◀─ 完了表示 ─│           │           │
```

---

### SD-003: ヘルスチェックフロー

```
監視システム    Backend    ChromaDB
     │             │           │
     │─ GET /health ─▶│         │
     │             │─ /api/v2/heartbeat ▶│
     │             │◀─ 200 OK ───────────│
     │◀─ {"status": "ok"} ──────│
```

---

### SD-004: mTLS通信フロー

```
Backend(Envoy Sidecar)    ChromaDB(Envoy Sidecar)
      │                            │
      │─ TLS ClientHello ─────────▶│
      │◀─ TLS ServerHello ─────────│
      │─ クライアント証明書（SPIFFE）▶│
      │◀─ サーバー証明書（SPIFFE）───│
      │─ 証明書検証（STRICT）        │
      │◀─ 証明書検証（STRICT）       │
      │─ 暗号化通信開始 ────────────▶│
```

---

### SD-005: CI/CDフロー

```
開発者    GitHub    Runner(Mac)    Docker    K8s
   │         │           │           │        │
   │─ Push ─▶│           │           │        │
   │         │─ Job実行 ─▶│           │        │
   │         │           │─ build ──▶│        │
   │         │           │─ test ───▶│        │
   │         │           │─ dry-run ──────────▶│
   │         │◀─ 結果 ────│           │        │
   │◀─ 通知 ──│           │           │        │
```
