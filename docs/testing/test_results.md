# Test Results
<div align="right">作成日: 2026-06-05</div>

## テスト結果

### 最新テスト結果サマリー

| 種別 | 実施日 | 合計 | 成功 | 失敗 | スキップ |
|------|--------|------|------|------|---------|
| Unitテスト | - | - | - | - | - |
| Integrationテスト | - | - | - | - | - |
| E2Eテスト | - | - | - | - | - |
| Performanceテスト | - | - | - | - | - |

> ※ テスト実施後に結果を記録してください。

---

### テスト結果記録テンプレート

```
## テスト実施記録

- 実施日:
- 実施者:
- ブランチ:
- コミットID:
- DEPLOY_ENV: compose / minikube / aks

### 結果サマリー

| 種別 | 合計 | 成功 | 失敗 |
|------|------|------|------|
| Unitテスト | | | |
| Integrationテスト | | | |

### 失敗テスト

| テストID | 内容 | エラー内容 | 対応 |
|---------|------|----------|------|
| | | | |

### カバレッジ

| 対象 | カバレッジ |
|------|----------|
| src/backend/app/ | % |
```

---

### CI実行結果確認方法

```bash
# GitHub ActionsのURL
https://github.com/redmine54/ai_chat/actions

# ローカルでテスト実行
docker build -t aichat:latest -f src/backend/Dockerfile .
docker run --rm aichat:latest python -m pytest tests/unit/ -v
docker run --rm aichat:latest python -m pytest tests/integration/ -v

# CI履歴の削除（最新1件残す）
gh run list --repo redmine54/ai_chat --limit 100 --json databaseId \
  -q '.[1:][].databaseId' | xargs -I {} gh run delete {} --repo redmine54/ai_chat
```
