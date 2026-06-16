# Test Results
<div align="right">作成日: 2026-06-05　最終更新: 2026-06-14</div>

## テスト結果

### 最新テスト結果サマリー

| 種別 | 実施日 | 合計 | 成功 | 失敗 | スキップ |
|------|--------|------|------|------|---------|
| Unitテスト | 2026-06-14 | 30 | 30 | 0 | 0 |
| Integrationテスト | 2026-06-14 | 12 | 12 | 0 | 0 |
| E2Eテスト | - | - | - | - | - |
| Performanceテスト | - | - | - | - | - |

---

### テスト結果記録

#### 実施情報

| 項目 | 内容 |
|------|------|
| 実施日 | 2026-06-14 |
| 実施者 | redmine54 |
| ブランチ | feature/redmine-140_aichat |
| コミットID | 2cb772f |
| DEPLOY_ENV | compose |

#### 結果サマリー

| 種別 | 合計 | 成功 | 失敗 |
|------|------|------|------|
| Unitテスト | 30 | 30 | 0 |
| Integrationテスト | 12 | 12 | 0 |
| **合計** | **42** | **42** | **0** |

#### 失敗テスト

なし

#### カバレッジ

| ファイル | 行数 | 未テスト行 | カバー率 |
|---------|------|-----------|---------|
| app/__init__.py | 0 | 0 | 100% |
| app/main.py | 200 | 105 | 48% |
| app/rag.py | 107 | 32 | 70% |
| **合計** | **307** | **137** | **55%** |

> ※ カバレッジ目標80%に対し現状55%。未テストのエンドポイント（/api/pdf/status、/api/pdf/delete、/api/sh/run、/api/ci/runs等）のテスト追加が必要。

---

### CI実行結果確認方法

```bash
# GitHub ActionsのURL
https://github.com/redmine54/ai_chat/actions

# ローカルでテスト実行
docker compose run --rm backend pytest tests/unit/ -v \
  --cov=app --cov-report=term-missing

docker compose run --rm backend pytest tests/integration/ -v

# CI履歴の削除（最新1件残す）
gh run list --repo redmine54/ai_chat --limit 100 --json databaseId \
  -q '.[1:][].databaseId' | xargs -I {} gh run delete {} --repo redmine54/ai_chat
```
