# Test Plan
<div align="right">作成日: 2026-06-05</div>

## テスト計画

### テスト方針

| 種別 | 目的 | 実行タイミング |
|------|------|--------------|
| Unitテスト | 個別関数・クラスの動作確認 | PR作成時（CI自動） |
| Integrationテスト | コンポーネント間の連携確認 | PR作成時（CI自動） |
| E2Eテスト | エンドツーエンドの動作確認 | リリース前（手動） |
| Performanceテスト | 性能・負荷確認 | リリース前（手動） |

---

### テスト対象

| コンポーネント | Unitテスト | Integrationテスト |
|--------------|-----------|-----------------|
| RAG処理 | ✅ | ✅ |
| ChromaDB連携（API v2） | ✅ | ✅ |
| LLM API連携 | ✅（Mock） | ✅ |
| REST API | ✅ | ✅ |
| PDFパース | ✅ | ✅ |

---

### テスト環境

| 種別 | 環境 |
|------|------|
| Unitテスト | ローカル・CI（Self-hosted Runner on Mac M1） |
| Integrationテスト | ローカル・CI（Self-hosted Runner on Mac M1） |
| E2Eテスト | Minikube |
| Performanceテスト | Minikube |

---

### テスト実行方法

```bash
# CI（GitHub Actions）での自動実行
git push origin feature/xxx  # → Self-hosted Runnerが自動実行

# ローカルでの手動実行
docker build -t aichat:latest -f src/backend/Dockerfile .
docker run --rm aichat:latest python -m pytest tests/unit/ -v
docker run --rm aichat:latest python -m pytest tests/integration/ -v
```

---

### カバレッジ目標

| 対象 | 目標カバレッジ |
|------|-------------|
| Unitテスト | 80%以上 |
| Integrationテスト | 主要フロー100% |

---

### テストツール

| ツール | 用途 |
|--------|------|
| pytest | Unitテスト・Integrationテスト |
| httpx | APIテスト |
| pytest-cov | カバレッジ計測 |
| locust | 負荷テスト |
