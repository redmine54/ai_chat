"""
pytest設定ファイル
全テスト共通のfixture・設定
"""
import os
import sys

# appモジュールをimportできるようにパスを追加
sys.path.insert(0, "/app")

# テスト用環境変数
os.environ.setdefault("GEMINI_API_KEY", "test_dummy_key")
os.environ.setdefault("CHROMA_HOST", "vectordb")
os.environ.setdefault("CHROMA_PORT", "8000")
