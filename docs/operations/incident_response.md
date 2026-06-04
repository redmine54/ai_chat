# Incident Response

## インシデント対応手順

### インシデントレベル定義

| レベル | 内容 | 対応時間 |
|--------|------|---------|
| P1 | システム全停止 | 即時対応 |
| P2 | 主要機能停止 | 1時間以内 |
| P3 | 一部機能停止 | 当日対応 |
| P4 | 軽微な問題 | 翌営業日対応 |

---

### 対応フロー

```
インシデント検知
        ↓
状態確認・レベル判定
        ↓
担当者へ連絡
        ↓
原因調査
        ↓
対応・復旧
        ↓
事後報告
```

---

### よくあるインシデントと対応

#### P1: チャットが完全に使えない

```bash
# 1. Pod状態確認
kubectl get pods -n aichat

# 2. ログ確認
kubectl logs -f deploy/backend -n aichat -c fastapi-app

# 3. 再起動
kubectl rollout restart deployment/backend -n aichat
kubectl rollout restart deployment/vectordb -n aichat
```

#### P2: ChromaDB接続エラー

```bash
# 1. ChromaDB Pod確認
kubectl get pods -n aichat | grep vectordb

# 2. ヘルスチェック
kubectl exec -it <backend-pod> -n aichat -c fastapi-app -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://vectordb-service:8000/api/v2/heartbeat').status)"

# 3. ChromaDB再起動
kubectl rollout restart deployment/vectordb -n aichat
```

#### P3: レスポンスが遅い

```bash
# リソース使用状況確認
kubectl top pods -n aichat

# Pod数を増やす
kubectl scale deployment/backend --replicas=2 -n aichat
```

---

### 事後報告テンプレート

```
## インシデント報告

- 発生日時:
- 復旧日時:
- 影響範囲:
- 原因:
- 対応内容:
- 再発防止策:
```
