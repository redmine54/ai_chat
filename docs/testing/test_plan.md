# Test Plan
<div align="right">作成日: 2026-06-05　最終更新: 2026-06-14</div>

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
docker compose run --rm backend pytest tests/unit/ -v \
  --cov=app --cov-report=xml --cov-report=term

docker compose run --rm backend pytest tests/integration/ -v

# カバレッジ詳細（未テスト行番号表示）
docker compose run --rm backend pytest tests/unit/ \
  --cov=app --cov-report=term-missing
```

---

### カバレッジ目標と現状

| 対象 | 目標 | 現状 | 状況 |
|------|------|------|------|
| Unitテスト | 80%以上 | 55% | ⚠️ 未達 |
| Integrationテスト | 主要フロー100% | 100% | ✅ 達成 |

**カバレッジ向上のために追加が必要なテスト：**

| エンドポイント | テストID |
|--------------|---------|
| GET /api/pdf/status | UT-040 |
| DELETE /api/pdf/delete | UT-041 |
| POST /api/sh/run | UT-042 |
| GET /api/ci/runs | UT-043 |
| GET /api/ci/runs/{id}/jobs | UT-044 |
| GET /api/ci/runs/{id}/logs/{job_id} | UT-045 |

---

### テストツール

| ツール | 用途 |
|--------|------|
| pytest | Unitテスト・Integrationテスト |
| pytest-cov | カバレッジ計測 |
| pytest-mock | モック |
| httpx | APIテスト |
| locust | 負荷テスト |
| trivy | Dockerイメージ脆弱性チェック |

---

### CI/CDパイプライン

```
push（feature/**）
  ↓
① フォーマットチェック（ruff format）
② Lintチェック（ruff check）
③ 型チェック（mypy）
④ Unitテスト（pytest + coverage）
⑤ Integrationテスト（pytest）
⑥ 脆弱性チェック（trivy）
  ↓
Pull Request → main へマージ
  ↓
手動デプロイ（workflow_dispatch: cd_only）
```
