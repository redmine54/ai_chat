#!/bin/bash

# ChromaDB保存状況確認スクリプト

unset DOCKER_HOST
docker context use desktop-linux > /dev/null 2>&1

echo "==============================="
echo " ChromaDB 保存状況確認"
echo "==============================="

docker compose exec -T backend python3 - <<'EOF'
import chromadb, os
from collections import defaultdict

def show_collection_detail(col):
    count = col.count()
    print(f"\n  コレクション: {col.name}  (総チャンク数: {count}件)")

    if count == 0:
        print("  　データなし")
        return

    # 全データ取得
    results = col.get(include=["documents", "metadatas"])
    metadatas = results.get("metadatas") or []
    documents = results.get("documents") or []

    # ドキュメント(source)ごとに集計
    doc_chunks = defaultdict(list)
    for meta, doc in zip(metadatas, documents):
        source = meta.get("source", "unknown")
        chunk = meta.get("chunk", "?")
        doc_chunks[source].append((chunk, doc))

    print(f"  ドキュメント数: {len(doc_chunks)}件")
    print()

    for source, chunks in sorted(doc_chunks.items()):
        total_chars = sum(len(doc) for _, doc in chunks)
        print(f"  📄 {source}")
        print(f"     チャンク数 : {len(chunks)}")
        print(f"     総文字数  : {total_chars:,}文字")
        # 最初のチャンクを冒頭プレビューとして表示
        first_doc = chunks[0][1] if chunks else ""
        preview = first_doc[:60].replace("\n", " ")
        print(f"     冒頭プレビュー: {preview}...")
        print()

# HttpClient（vectordbコンテナ）
host = os.getenv("CHROMA_HOST", "vectordb")
port = int(os.getenv("CHROMA_PORT", 8000))
try:
    client = chromadb.HttpClient(host=host, port=port)
    cols = client.list_collections()
    print(f"[HttpClient / vectordb] コレクション数: {len(cols)}")
    for c in cols:
        col = client.get_collection(c.name)
        show_collection_detail(col)
except Exception as e:
    print(f"[HttpClient] 接続失敗: {e}")

# PersistentClient（ローカルボリューム）
try:
    client2 = chromadb.PersistentClient(path="/app/chroma")
    cols2 = client2.list_collections()
    print(f"\n[PersistentClient / local] コレクション数: {len(cols2)}")
    for c in cols2:
        col2 = client2.get_collection(c.name)
        show_collection_detail(col2)
except Exception as e:
    print(f"[PersistentClient] 接続失敗: {e}")
EOF

echo "==============================="
