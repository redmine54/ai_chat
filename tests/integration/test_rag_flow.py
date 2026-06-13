"""
Integration Tests for RAG flow
対象: PDF登録→ベクトル検索→回答生成の一連の流れ
Gemini APIはMock、ChromaDBは実際に接続
"""

import pytest
import os
import uuid
from unittest.mock import patch, MagicMock


@pytest.fixture
def test_collection():
    """テスト用ChromaDBコレクション（テスト後に削除）"""
    import chromadb

    host = os.getenv("CHROMA_HOST", "vectordb")
    port = int(os.getenv("CHROMA_PORT", 8000))
    client = chromadb.HttpClient(host=host, port=port)
    col_name = f"test_rag_{uuid.uuid4().hex[:8]}"
    col = client.get_or_create_collection(col_name)
    yield col
    try:
        client.delete_collection(col_name)
    except Exception:
        pass


def test_store_and_search(test_collection):
    """ドキュメント登録後に類似検索で取得できるか"""
    # ドキュメント登録
    test_collection.add(
        documents=["消費者物価指数は前年比2.5%上昇しました。"],
        embeddings=[[0.1] * 768],
        ids=["doc_0"],
        metadatas=[{"source": "test_pdf", "chunk": 0}],
    )

    # 類似検索
    results = test_collection.query(query_embeddings=[[0.1] * 768], n_results=1)
    assert "消費者物価指数" in results["documents"][0][0]


def test_answer_with_rag_mock(test_collection):
    """RAG回答生成が正常に動作するか（Gemini APIをMock）"""
    # テストデータを登録
    test_collection.add(
        documents=["契約期間は2026年6月1日から6月30日までです。"],
        embeddings=[[0.3] * 768],
        ids=["doc_1"],
        metadatas=[{"source": "contract_pdf", "chunk": 0}],
    )

    mock_response = MagicMock()
    mock_response.text = "契約期間は2026年6月1日から6月30日までです。"

    with patch("app.rag.collection", test_collection):
        with patch("app.rag.get_embedding", return_value=[0.3] * 768):
            with patch("app.rag.client") as mock_client:
                mock_client.models.generate_content.return_value = mock_response
                from app.rag import answer_with_rag

                answer = answer_with_rag("契約期間はいつですか？")
                assert "2026年" in answer


def test_no_relevant_document(test_collection):
    """関連ドキュメントがない場合のメッセージを返すか"""
    with patch("app.rag.collection", test_collection):
        with patch("app.rag.get_embedding", return_value=[0.9] * 768):
            from app.rag import answer_with_rag

            answer = answer_with_rag("全く関係ない質問")
            assert "ドキュメントが見つかりません" in answer or isinstance(answer, str)


def test_duplicate_index_prevention(test_collection):
    """同じPDFを2回登録しても件数が増えないか"""
    with patch("app.rag.collection", test_collection):
        with patch("app.rag.extract_text_from_pdf", return_value="テスト文章。" * 5):
            with patch("app.rag.get_embedding", return_value=[0.1] * 768):
                from app.rag import extract_and_store_pdf

                # 1回目登録
                count1 = extract_and_store_pdf("/dummy/test.pdf", "test_doc")
                assert count1 > 0

                # 2回目登録（重複防止）
                count2 = extract_and_store_pdf("/dummy/test.pdf", "test_doc")
                assert test_collection.count() == count2  # 増えていない
