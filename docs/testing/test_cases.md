# Test Cases
<div align="right">作成日: 2026-06-05　最終更新: 2026-06-14</div>

## テストケース一覧

### TC-001: Unitテスト

#### TC-001-1: APIエンドポイントテスト（test_api.py）

| テストID | テスト関数名 | テスト内容 | 期待結果 |
|---------|------------|----------|---------|
| UT-020 | test_health_check | GET /health | 200 OK `{"status": "ok"}` |
| UT-021 | test_pdf_list_returns_files | GET /api/pdf/list（PDFあり） | 200 OK ファイル一覧返却 |
| UT-022 | test_pdf_list_empty | GET /api/pdf/list（PDFなし） | 200 OK 空リスト返却 |
| UT-023 | test_chat_valid_message | POST /api/chat（正常メッセージ） | 200 OK 回答返却 |
| UT-024 | test_chat_empty_message | POST /api/chat（空メッ�セージ） | 200 / 422 / 500 |
| UT-025 | test_chat_missing_message | POST /api/chat（messageフィールドなし） | 422 Unprocessable Entity |
| UT-026 | test_chat_rag_error_returns_500 | POST /api/chat（RAGエラー） | 500 Internal Server Error |
| UT-027 | test_index_nonexistent_file_returns_404 | POST /api/pdf/index（存在しないファイル） | 404 Not Found |
| UT-028 | test_index_non_pdf_returns_400 | POST /api/pdf/index（PDF以外） | 400 Bad Request |
| UT-029 | test_index_valid_pdf | POST /api/pdf/index（正常PDF） | 200 OK chunk数返却 |

#### TC-001-2: RAG処理テスト（test_rag.py）

| テストID | テスト関数名 | テスト内容 | 期待結果 |
|---------|------------|----------|---------|
| UT-001 | test_split_into_sentences_basic | 文分割の基本動作（句点） | 正しく分割される |
| UT-002 | test_split_into_sentences_empty | 空文字の分割 | 空リスト返却 |
| UT-003 | test_split_into_sentences_exclamation | ！での文分割 | 正しく分割される |
| UT-004 | test_split_into_sentences_question | ？での文分割 | 正しく分割される |
| UT-005 | test_chunk_sentences_within_limit | 制限内のチャンク化（500文字） | 1チャンクとして返却 |
| UT-006 | test_chunk_sentences_exceeds_limit | 制限超えのチャンク化 | 複数チャンクに分割 |
| UT-007 | test_chunk_sentences_empty | 空のチャンク化 | 空リスト返却 |
| UT-008 | test_chunk_sentences_single_long | 1文が制限超えの場合 | 1チャンクとして返却 |
| UT-009 | test_get_embedding_returns_list | 埋め込みベクトル生成 | リスト形式で返却 |
| UT-010 | test_get_embedding_retry_on_failure | 失敗時のリトライ | リトライ後に成功 |
| UT-011 | test_get_embedding_raises_after_max_retry | リトライ上限後のエラー | 例外発生 |
| UT-012 | test_extract_and_store_pdf_empty_text | 空PDFの処理 | 0チャンク返却 |
| UT-013 | test_extract_and_store_pdf_returns_chunk_count | chunk数の返却 | 正しいchunk数返却 |

#### TC-001-3: リクエストモデルテスト（test_schema.py）

| テストID | テスト関数名 | テスト内容 | 期待結果 |
|---------|------------|----------|---------|
| UT-030 | test_chat_request_valid | ChatRequestの基本生成 | 正常に生成 |
| UT-031 | test_chat_request_with_model | ChatRequestにmodel指定 | 指定モデルで生成 |
| UT-032 | test_chat_request_default_model | ChatRequestのデフォルトモデル | gemini-2.5-flash |
| UT-033 | test_index_request_valid | IndexRequestの基本生成 | 正常に生成 |
| UT-034 | test_index_request_force_default_false | IndexRequestのforceデフォルト | False |
| UT-035 | test_index_request_force_true | IndexRequestにforce=True指定 | True |
| UT-036 | test_delete_request_valid | DeleteRequestの基本生成 | 正常に生成 |

---

### TC-002: Integrationテスト

#### TC-002-1: ChromaDB接続テスト（test_chromadb.py）

| テストID | テスト関数名 | テスト内容 | 期待結果 |
|---------|------------|----------|---------|
| IT-001 | test_chromadb_connection | ChromaDBへの接続確認 | 接続成功 |
| IT-002 | test_chromadb_list_collections | コレクション一覧取得 | リスト返却 |
| IT-003 | test_collection_create_and_count | コレクション作成と件数確認 | 0件 |
| IT-004 | test_collection_add_and_count | データ追加と件数確認 | 追加件数返却 |
| IT-005 | test_collection_add_and_retrieve | データ追加と取得 | 追加データ取得成功 |
| IT-006 | test_collection_query | コレクションへのクエリ | 検索結果返却 |
| IT-007 | test_collection_delete | データ削除 | 削除後0件 |
| IT-008 | test_duplicate_prevention | 重複登録防止 | 重複なし |

#### TC-002-2: RAGフローテスト（test_rag_flow.py）

| テストID | テスト関数名 | テスト内容 | 期待結果 |
|---------|------------|----------|---------|
| IT-009 | test_store_and_search | データ保存と検索 | 保存データが検索でヒット |
| IT-010 | test_answer_with_rag_mock | RAGによる回答生成（モック） | 回答文字列返却 |
| IT-011 | test_no_relevant_document | 関連文書なしの回答 | デフォルト回答返却 |
| IT-012 | test_duplicate_index_prevention | 重複インデックス防止 | 重複なし |

---

### TC-003: E2Eテスト（未実施）

| テストID | テスト内容 | 期待結果 |
|---------|----------|---------|
| E2E-001 | チャット画面表示 | 画面が正常表示される |
| E2E-002 | 質問入力→回答表示 | 回答が表示される |
| E2E-003 | PDFアップロード | アップロード完了が表示される |
| E2E-004 | /specsドキュメントビューア | mdが正常表示される |

---

### TC-004: Performanceテスト（未実施）

| テストID | テスト内容 | 合格基準 |
|---------|----------|---------|
| PT-001 | 同時10ユーザーでのチャット | 応答時間30秒以内 |
| PT-002 | 1000件のベクトル検索 | 検索時間3秒以内 |
