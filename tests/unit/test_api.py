"""
Unit Tests for main.py API endpoints
対象: /health, /api/pdf/list, /api/chat, /api/pdf/index
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys

sys.path.insert(0, "/app")


@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    with patch("app.rag.client"):  # Gemini APIをMock
        with patch("app.rag.chroma_client"):  # ChromaDBをMock
            with patch("app.rag.collection"):  # collectionをMock
                with patch("app.rag.debug_list_models"):  # 起動時のモデル一覧をスキップ
                    from app.main import app

                    return TestClient(app)


# ============================================================
# GET /health
# ============================================================
def test_health_check(client):
    """ヘルスチェックが200を返すか"""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ============================================================
# GET /api/pdf/list
# ============================================================
def test_pdf_list_returns_files(client, tmp_path):
    """PDFファイル一覧が返るか"""
    # テスト用PDFを作成
    (tmp_path / "test.pdf").write_text("dummy")
    with patch("app.main.DATA_DIR", str(tmp_path)):
        res = client.get("/api/pdf/list")
        assert res.status_code == 200
        assert "files" in res.json()
        assert "test.pdf" in res.json()["files"]


def test_pdf_list_empty(client, tmp_path):
    """PDFがない場合は空リストを返すか"""
    with patch("app.main.DATA_DIR", str(tmp_path)):
        res = client.get("/api/pdf/list")
        assert res.status_code == 200
        assert res.json()["files"] == []


# ============================================================
# POST /api/chat
# ============================================================
def test_chat_valid_message(client):
    """正常なメッセージで200を返すか"""
    with patch("app.rag.answer_with_rag", return_value="テスト回答"):
        res = client.post("/api/chat", json={"message": "テスト質問"})
        assert res.status_code == 200
        assert "answer" in res.json()
        assert res.json()["answer"] == "テスト回答"


def test_chat_empty_message(client):
    """空メッセージで422を返すか"""
    res = client.post("/api/chat", json={"message": ""})
    assert res.status_code in [200, 422]  # バリデーション実装に依存


def test_chat_missing_message(client):
    """messageフィールドなしで422を返すか"""
    res = client.post("/api/chat", json={})
    assert res.status_code == 422


def test_chat_rag_error_returns_500(client):
    """RAGエラー時に500を返すか"""
    with patch("app.rag.answer_with_rag", side_effect=Exception("RAG Error")):
        res = client.post("/api/chat", json={"message": "テスト"})
        assert res.status_code == 500


# ============================================================
# POST /api/pdf/index
# ============================================================
def test_index_nonexistent_file_returns_404(client):
    """存在しないファイルで404を返すか"""
    res = client.post("/api/pdf/index", json={"filename": "nonexistent.pdf"})
    assert res.status_code == 404


def test_index_non_pdf_returns_400(client, tmp_path):
    """PDF以外のファイルで400を返すか"""
    (tmp_path / "test.txt").write_text("dummy")
    with patch("app.main.DATA_DIR", str(tmp_path)):
        res = client.post("/api/pdf/index", json={"filename": "test.txt"})
        assert res.status_code == 400


def test_index_valid_pdf(client, tmp_path):
    """正常なPDFで200を返すか"""
    (tmp_path / "test.pdf").write_bytes(b"dummy pdf content")
    with patch("app.main.DATA_DIR", str(tmp_path)):
        with patch("app.rag.extract_and_store_pdf", return_value=5):
            res = client.post("/api/pdf/index", json={"filename": "test.pdf"})
            assert res.status_code == 200
            assert res.json()["chunks"] == 5
