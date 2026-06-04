# Release Procedure

## リリース手順

### リリースフロー

```
featureブランチで開発
        ↓
Pull Request作成（feature → main）
        ↓
CI自動実行（GitHub Actions）
  - Dockerビルド
  - Unitテスト
  - Integrationテスト
  - K8sマニフェスト検証
        ↓ CI成功
コードレビュー
        ↓ 承認
mainブランチへマージ
        ↓
ArgoCD自動デプロイ
```

---

### ブランチ命名規則

| 種別 | 命名規則 | 例 |
|------|---------|-----|
| 機能追加 | feature/redmine-{番号}-{内容} | feature/redmine-123-ai_chat |
| バグ修正 | fix/redmine-{番号}-{内容} | fix/redmine-124-chat_error |
| 緊急修正 | hotfix/{内容} | hotfix/critical_bug |

---

### リリース前チェックリスト

- [ ] CIが全て成功しているか
- [ ] コードレビューが完了しているか
- [ ] テストが全て成功しているか
- [ ] ドキュメントが更新されているか
- [ ] `.gitignore`に不要なファイルが含まれていないか

---

### ロールバック手順

```bash
# ArgoCDで前バージョンに戻す
argocd app rollback aichat

# または手動でイメージタグを変更
kubectl set image deployment/backend \
  fastapi-app=aichat:前バージョンのタグ -n aichat
```

---

### リリース記録

| バージョン | 日付 | 内容 |
|-----------|------|------|
| v0.1.0 | 2025-05-29 | 初期構築 |
| v0.2.0 | 2025-06-03 | mTLS・CI/CD追加 |
