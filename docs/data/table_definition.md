# Table Definition
<div align="right">作成日: 2026-06-05</div>

## データ定義

### ChromaDB コレクション定義

#### documents コレクション

```python
collection = client.create_collection(
    name="pdf_documents",
    metadata={"hnsw:space": "cosine"}
)
```

**フィールド定義:**

| フィールド | 型 | 必須 | 説明 | 例 |
|-----------|-----|------|------|-----|
| id | string | ✅ | チャンクID（UUID） | "abc123-..." |
| embedding | list[float] | ✅ | ベクトル（1536次元） | [0.1, 0.2, ...] |
| document | string | ✅ | テキスト内容 | "社内規程第1条..." |
| metadata.source | string | ✅ | PDFファイル名 | "manual.pdf" |
| metadata.page | integer | ✅ | ページ番号 | 3 |
| metadata.chunk_index | integer | ✅ | チャンクインデックス | 0 |
| metadata.created_at | string | ✅ | 登録日時（ISO8601） | "2026-06-05T00:00:00Z" |

---

### 環境変数定義

#### Backend

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| CHROMA_HOST | vectordb | ChromaDBのホスト名 |
| CHROMA_PORT | 8000 | ChromaDBのポート番号 |
| COLLECTION_NAME | pdf_documents | ChromaDBのコレクション名 |
| CHUNK_SIZE | 500 | チャンクサイズ（文字数） |
| CHUNK_OVERLAP | 50 | チャンクオーバーラップ（文字数） |
| TOP_K | 5 | 検索結果の最大取得件数 |

#### ChromaDB

| 変数名 | 値 | 説明 |
|--------|-----|------|
| IS_PERSISTENT | TRUE | データ永続化の有効化 |

---

### ポート定義

| サービス | 内部ポート | 外部ポート（docker compose） |
|---------|-----------|---------------------------|
| frontend | 80 | 80 |
| backend | 8000 | 8000 |
| vectordb | 8000 | 8001 |
