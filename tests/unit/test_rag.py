"""
Unit Tests for rag.py
対象: split_into_sentences, chunk_sentences, get_embedding（mock）
"""

import pytest
from unittest.mock import MagicMock, patch


# ============================================================
# split_into_sentences のテスト
# ============================================================
def test_split_into_sentences_basic():
    """句読点で正しく分割されるか"""
    from app.rag import split_into_sentences

    text = "これはテストです。次の文章です。最後の文です。"
    result = split_into_sentences(text)
    assert len(result) == 3
    assert result[0] == "これはテストです。"


def test_split_into_sentences_empty():
    """空文字列は空リストを返すか"""
    from app.rag import split_into_sentences

    result = split_into_sentences("")
    assert result == []


def test_split_into_sentences_exclamation():
    """！で分割されるか"""
    from app.rag import split_into_sentences

    text = "すごい！本当に！"
    result = split_into_sentences(text)
    assert len(result) == 2


def test_split_into_sentences_question():
    """？で分割されるか"""
    from app.rag import split_into_sentences

    text = "これは何？あれは何？"
    result = split_into_sentences(text)
    assert len(result) == 2


# ============================================================
# chunk_sentences のテスト
# ============================================================
def test_chunk_sentences_within_limit():
    """500文字以内なら1チャンクにまとまるか"""
    from app.rag import chunk_sentences

    sentences = ["短い文。"] * 5
    result = chunk_sentences(sentences, max_chars=500)
    assert len(result) == 1


def test_chunk_sentences_exceeds_limit():
    """500文字を超えたら複数チャンクに分割されるか"""
    from app.rag import chunk_sentences

    sentences = ["あ" * 200 + "。"] * 5  # 各201文字
    result = chunk_sentences(sentences, max_chars=500)
    assert len(result) > 1


def test_chunk_sentences_empty():
    """空リストは空リストを返すか"""
    from app.rag import chunk_sentences

    result = chunk_sentences([])
    assert result == []


def test_chunk_sentences_single_long():
    """1文が制限を超える場合も1チャンクとして返すか"""
    from app.rag import chunk_sentences

    sentences = ["あ" * 1000 + "。"]
    result = chunk_sentences(sentences, max_chars=500)
    assert len(result) == 1


# ============================================================
# get_embedding のテスト（Gemini APIをMock）
# ============================================================
def test_get_embedding_returns_list():
    """ベクトル化が正常にリストを返すか"""
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1, 0.2, 0.3]

    mock_result = MagicMock()
    mock_result.embeddings = [mock_embedding]

    with patch("app.rag.client") as mock_client:
        mock_client.models.embed_content.return_value = mock_result
        from app.rag import get_embedding

        result = get_embedding("テストテキスト")
        assert result == [0.1, 0.2, 0.3]


def test_get_embedding_retry_on_failure():
    """失敗時にリトライするか（2回失敗→3回目成功）"""
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1, 0.2, 0.3]
    mock_result = MagicMock()
    mock_result.embeddings = [mock_embedding]

    with patch("app.rag.client") as mock_client:
        with patch("app.rag.time.sleep"):  # sleepをスキップ
            mock_client.models.embed_content.side_effect = [
                Exception("API Error"),
                Exception("API Error"),
                mock_result,
            ]
            from app.rag import get_embedding

            result = get_embedding("テスト", retry=3)
            assert result == [0.1, 0.2, 0.3]
            assert mock_client.models.embed_content.call_count == 3


def test_get_embedding_raises_after_max_retry():
    """最大リトライ回数を超えたら例外を発生させるか"""
    with patch("app.rag.client") as mock_client:
        with patch("app.rag.time.sleep"):
            mock_client.models.embed_content.side_effect = Exception("API Error")
            from app.rag import get_embedding

            with pytest.raises(Exception):
                get_embedding("テスト", retry=3)


# ============================================================
# extract_and_store_pdf のテスト（ChromaDB・Gemini APIをMock）
# ============================================================
def test_extract_and_store_pdf_empty_text():
    """テキストが空のPDFはValueErrorを発生させるか"""
    with patch("app.rag.extract_text_from_pdf", return_value=""):
        from app.rag import extract_and_store_pdf

        with pytest.raises(ValueError, match="テキストを抽出できませんでした"):
            extract_and_store_pdf("/dummy/path.pdf", "dummy_id")


def test_extract_and_store_pdf_returns_chunk_count():
    """正常時にチャンク数を返すか"""
    with patch("app.rag.extract_text_from_pdf", return_value="テスト文章。" * 10):
        with patch("app.rag.get_embedding", return_value=[0.1] * 768):
            with patch("app.rag.collection") as mock_col:
                mock_col.get.return_value = {"ids": []}
                from app.rag import extract_and_store_pdf

                result = extract_and_store_pdf("/dummy/path.pdf", "dummy_id")
                assert isinstance(result, int)
                assert result > 0
                mock_col.add.assert_called_once()
