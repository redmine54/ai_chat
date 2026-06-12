"""
Unit Tests for Pydantic schemas
対象: ChatRequest, IndexRequest, DeleteRequest
"""

import pytest


def test_chat_request_valid():
    """ChatRequestが正常に生成されるか"""
    from app.main import ChatRequest

    req = ChatRequest(message="テスト質問")
    assert req.message == "テスト質問"


def test_chat_request_with_model():
    """ChatRequestにmodelを指定できるか"""
    from app.main import ChatRequest

    req = ChatRequest(message="テスト", model="models/gemini-2.0-flash")
    assert req.model == "models/gemini-2.0-flash"


def test_chat_request_default_model():
    """ChatRequestのデフォルトモデルが設定されているか"""
    from app.main import ChatRequest

    req = ChatRequest(message="テスト")
    assert req.model is not None


def test_index_request_valid():
    """IndexRequestが正常に生成されるか"""
    from app.main import IndexRequest

    req = IndexRequest(filename="test.pdf")
    assert req.filename == "test.pdf"


def test_index_request_force_default_false():
    """IndexRequestのforceのデフォルトはFalseか"""
    from app.main import IndexRequest

    req = IndexRequest(filename="test.pdf")
    assert not req.force


def test_index_request_force_true():
    """IndexRequestにforce=Trueを指定できるか"""
    from app.main import IndexRequest

    req = IndexRequest(filename="test.pdf", force=True)
    assert req.force


def test_delete_request_valid():
    """DeleteRequestが正常に生成されるか"""
    from app.main import DeleteRequest

    req = DeleteRequest(document_id="test_doc")
    assert req.document_id == "test_doc"
