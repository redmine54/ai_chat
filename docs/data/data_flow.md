# Data Flow
<div align="right">作成日: 2026-06-05</div>

## データフロー

### DF-001: PDFインデックス作成フロー

```
[PDFファイル]
     ↓
[テキスト抽出]
  - pypdfでテキスト抽出
  - ページ単位で処理
     ↓
[チャンク分割]
  - chunk_size: 500文字
  - chunk_overlap: 100文字
     ↓
[ベクトル化（Embedding）]
  - Embedding Modelでベクトル化
  - 1536次元ベクトル生成
     ↓
[ChromaDB保存]
  - コレクション: documents
  - API: /api/v2
  - ID: UUID
  - メタデータ: source, page, chunk_index
```

---

### DF-002: チャット処理フロー

```
[ユーザーの質問]
     ↓
[質問のベクトル化]
  - Embedding Modelでベクトル化
     ↓
[ChromaDB検索]
  - コサイン類似度で検索
  - TOP_K=5件取得
     ↓
[プロンプト生成]
  - システムプロンプト
  - 関連ドキュメント（コンテキスト）
  - ユーザーの質問
     ↓
[LLM API呼び出し]
  - プロンプトを送信
  - 回答を受信
     ↓
[レスポンス生成]
  - 回答テキスト
  - 参照ドキュメント情報
     ↓
[ユーザーへ返却]
```

---

### DF-003: データ永続化フロー

```
[ChromaDB（コンテナ内）]
     ↓ マウント
[PersistentVolume]
  - docker compose: chroma-dataボリューム
  - Minikube: hostPath
  - AKS: Azure Disk
```

---

### DF-004: CI/CDフロー

```
[featureブランチへPush]
     ↓
[GitHub Actions（Self-hosted Runner）]
  - Dockerイメージビルド
  - Unitテスト
  - Integrationテスト
  - K8sマニフェスト検証（minikube/aksモード）
     ↓
[mainへマージ]
     ↓
[ArgoCD自動デプロイ]
```

---

### データ保持期間

| データ | 保持期間 | 場所 |
|--------|---------|------|
| PDFベクトルデータ | 永続 | ChromaDB（PV） |
| チャット履歴 | 未実装 | - |
| ログ | 30日 | ファイル |
