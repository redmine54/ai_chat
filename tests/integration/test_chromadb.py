"""
Integration Tests for ChromaDB
対象: backendとvectordbの実際の通信
環境: docker compose up -d が必要
"""

import pytest
import os
import uuid


@pytest.fixture
def chroma_client():
    """ChromaDBクライアントを返すfixture"""
    import chromadb

    host = os.getenv("CHROMA_HOST", "vectordb")
    port = int(os.getenv("CHROMA_PORT", 8000))
    return chromadb.HttpClient(host=host, port=port)


@pytest.fixture
def test_collection(chroma_client):
    """テスト用コレクションを作成し、テスト後に削除するfixture"""
    col_name = f"test_{uuid.uuid4().hex[:8]}"
    col = chroma_client.get_or_create_collection(col_name)
    yield col
    try:
        chroma_client.delete_collection(col_name)
    except Exception:
        pass


# ============================================================
# 接続テスト
# ============================================================
def test_chromadb_connection(chroma_client):
    """ChromaDBに接続できるか"""
    import urllib.request

    host = os.getenv("CHROMA_HOST", "vectordb")
    port = int(os.getenv("CHROMA_PORT", 8000))
    res = urllib.request.urlopen(f"http://{host}:{port}/api/v2/heartbeat", timeout=5)
    assert res.status == 200


def test_chromadb_list_collections(chroma_client):
    """コレクション一覧を取得できるか"""
    cols = chroma_client.list_collections()
    assert isinstance(cols, list)


# ============================================================
# コレクション操作テスト
# ============================================================
def test_collection_create_and_count(test_collection):
    """コレクション作成後の件数が0か"""
    assert test_collection.count() == 0


def test_collection_add_and_count(test_collection):
    """ドキュメントを追加後に件数が増えるか"""
    test_collection.add(
        documents=["テストドキュメント"],
        embeddings=[[0.1] * 768],
        ids=["test_id_1"],
        metadatas=[{"source": "test"}],
    )
    assert test_collection.count() == 1


def test_collection_add_and_retrieve(test_collection):
    """追加したドキュメントを取得できるか"""
    test_collection.add(
        documents=["テスト内容"],
        embeddings=[[0.1] * 768],
        ids=["test_id_2"],
        metadatas=[{"source": "test", "chunk": 0}],
    )
    result = test_collection.get(ids=["test_id_2"])
    assert result["documents"][0] == "テスト内容"
    assert result["metadatas"][0]["source"] == "test"


def test_collection_query(test_collection):
    """ベクトル検索が動作するか"""
    test_collection.add(
        documents=["検索テスト文書"],
        embeddings=[[0.5] * 768],
        ids=["test_id_3"],
        metadatas=[{"source": "test"}],
    )
    results = test_collection.query(query_embeddings=[[0.5] * 768], n_results=1)
    assert len(results["documents"][0]) == 1
    assert results["documents"][0][0] == "検索テスト文書"


def test_collection_delete(test_collection):
    """ドキュメントを削除できるか"""
    test_collection.add(
        documents=["削除テスト"],
        embeddings=[[0.1] * 768],
        ids=["test_id_4"],
        metadatas=[{"source": "test"}],
    )
    assert test_collection.count() == 1
    test_collection.delete(ids=["test_id_4"])
    assert test_collection.count() == 0


def test_duplicate_prevention(test_collection):
    """同じsourceのドキュメントを削除してから再登録しても件数が増えないか"""
    # 初回登録
    test_collection.add(
        documents=["初回登録"],
        embeddings=[[0.1] * 768],
        ids=["dup_0"],
        metadatas=[{"source": "dup_test", "chunk": 0}],
    )
    assert test_collection.count() == 1

    # 既存データを削除してから再登録
    existing = test_collection.get(where={"source": "dup_test"})
    if existing["ids"]:
        test_collection.delete(ids=existing["ids"])
    test_collection.add(
        documents=["再登録"],
        embeddings=[[0.2] * 768],
        ids=["dup_0"],
        metadatas=[{"source": "dup_test", "chunk": 0}],
    )
    assert test_collection.count() == 1
