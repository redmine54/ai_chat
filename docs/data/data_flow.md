# Data Flow

## データフロー

### DF-001: PDFインデックス作成フロー

```
[PDFファイル]
     ↓
[テキスト抽出]
  - PyPDF2でテキスト抽出
  - ページ単位で処理
     ↓
[チャンク分割]
  - chunk_size: 500文字
  - chunk_overlap: 50文字
     ↓
[ベクトル化（Embedding）]
  - Embedding Modelでベクトル化
  - 1536次元ベクトル生成
     ↓
[ChromaDB保存]
  - コレクション: documents
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
  - Minikube: hostPath
  - AKS: Azure Disk
```

---

### データ保持期間

| データ | 保持期間 | 場所 |
|--------|---------|------|
| PDFベクトルデータ | 永続 | ChromaDB（PV） |
| チャット履歴 | 未実装 | - |
| ログ | 30日 | ファイル |
