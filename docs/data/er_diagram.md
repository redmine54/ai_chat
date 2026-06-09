# ER Diagram
<div align="right">作成日: 2026-06-05</div>

## データ設計

本システムはRDBMSを使用せず、ChromaDBをベクトルデータストアとして使用します。
ChromaDB APIはv2を使用しています（v1は廃止済み）。

---

### ChromaDBコレクション設計

#### コレクション: pdf_documents

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | チャンクの一意識別子（UUID） |
| embedding | vector | テキストのベクトル表現（1536次元） |
| document | string | チャンクのテキスト内容 |
| metadata | object | メタデータ |

**metadata構造:**

| フィールド | 型 | 説明 |
|-----------|-----|------|
| source | string | 元PDFファイル名 |
| page | integer | PDFのページ番号 |
| chunk_index | integer | チャンクのインデックス |
| created_at | string | 登録日時（ISO8601） |

---

### チャット履歴（将来実装）

#### コレクション: chat_history

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | メッセージの一意識別子 |
| user_id | string | ユーザーID |
| role | string | user / assistant |
| content | string | メッセージ内容 |
| created_at | string | 作成日時 |

---

### ChromaDB接続確認

```python
# ヘルスチェック（API v2）
import urllib.request
status = urllib.request.urlopen('http://vectordb-service:8000/api/v2/heartbeat').status
# → 200
```

---

### データフロー概念図

```
PDF → テキスト抽出 → チャンク分割 → ベクトル化 → ChromaDB（/api/v2）
                                                      ↑
質問 → ベクトル化 ─────────────────────────────── 類似検索
                                                      ↓
                                              関連チャンク取得
                                                      ↓
                                              LLM → 回答生成
```
