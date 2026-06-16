# Data Flow
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-14</div>

## データフロー

### DF-001: PDFインデックス作成フロー

```
[PDFファイル]
  src/backend/data/ 配下（.gitignore対象・ローカルのみ）
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
  - Gemini gemini-embedding-2でベクトル化
     ↓
[ChromaDB保存]
  - コレクション: pdf_documents
  - API: /api/v2
  - ID: UUID
  - メタデータ: source, page, chunk_index, registered_at
```

---

### DF-002: チャット処理フロー

```
[ユーザーの質問]
     ↓
[質問のベクトル化]
  - Gemini gemini-embedding-2でベクトル化
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
  - Gemini gemini-2.5-flash（デフォルト）
  - プロンプトを送信・回答を受信
     ↓
[レスポンス生成]
  - 回答テキスト（Markdown形式）
     ↓
[ユーザーへ返却]
  - チャット画面でMarkdownレンダリング表示
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
[GitHub Actions（Self-hosted Runner on Mac M1）]
  - フォーマット・Lint・型チェック（ruff・mypy）
  - Unitテスト（30件）・カバレッジ計測
  - Integrationテスト（12件）
  - Dockerイメージ脆弱性チェック（Trivy・.trivyignore適用）
  - K8sマニフェスト検証（minikube/aksモード）
     ↓
[Pull Request → mainへマージ]
     ↓
[手動デプロイ（workflow_dispatch: cd_only）]
  - docker compose up -d
```

---

### DF-005: 外部公開フロー（ユーザーレビュー用）

```
[compose環境]
  docker compose up -d
     ↓
[ngrok http 80]
  - ポート80（Nginx）をトンネル
  - https://xxxx.ngrok-free.dev でアクセス可能
     ↓
[外部ユーザーがブラウザでアクセス]
  - ngrok警告画面 → Visit Site → チャット画面
```

---

### データ保持期間

| データ | 保持期間 | 場所 |
|--------|---------|------|
| PDFベクトルデータ | 永続 | ChromaDB（PV） |
| PDFファイル | 永続 | src/backend/data/（ローカルのみ・gitignore対象） |
| チャット履歴 | 未実装 | - |
| ログ | 30日 | ファイル |
| CIカバレッジレポート | CIごと | GitHub Actions Artifacts |
