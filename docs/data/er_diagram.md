# ER Diagram

## データ設計

本システムはRDBMSを使用せず、ChromaDBをベクトルデータストアとして使用します。

---

### ChromaDBコレクション設計

#### コレクション: documents

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | チャンクの一意識別子 |
| embedding | vector | テキストのベクトル表現 |
| document | string | チャンクのテキスト内容 |
| metadata | object | メタデータ |

**metadata構造:**

| フィールド | 型 | 説明 |
|-----------|-----|------|
| source | string | 元PDFファイル名 |
| page | integer | PDFのページ番号 |
| chunk_index | integer | チャンクのインデックス |
| created_at | string | 登録日時 |

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

### データフロー概念図

```
PDF → テキスト抽出 → チャンク分割 → ベクトル化 → ChromaDB
                                                      ↑
質問 → ベクトル化 ─────────────────────────────── 類似検索
                                                      ↓
                                              関連チャンク取得
                                                      ↓
                                              LLM → 回答生成
```
