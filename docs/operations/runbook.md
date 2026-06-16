# Runbook
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-14</div>

## 運用手順書

### 日常運用

#### システム起動（docker composeモード）

```bash
docker compose up -d
```

| サービス | URL |
|---------|-----|
| チャット画面 | http://localhost |
| バックエンド API | http://localhost:8000/swagger/docs |
| ドキュメントビューア | http://localhost/api/specs |
| PDFインデクサー | http://localhost/api/indexer |
| ChromaDB | http://localhost:8001 |

#### ヘルスチェック

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

#### GitHub Actions Runner起動

```bash
cd ~/git_lesson/ai_chat/actions-runner
./run.sh &
```

**Runnerの状態確認:**

```bash
ps aux | grep Runner.Listener | grep -v grep
```

**Runnerの再起動:**

```bash
kill -9 $(pgrep -f Runner.Listener)
cd ~/git_lesson/ai_chat/actions-runner
./run.sh &
```

---

### CI/CDの手動実行

#### CIのみ実行（テスト）

```bash
git push origin feature/xxx  # → 自動でCIが起動
```

#### 手動でモードを選択して実行

GitHub → Actions → CI → Run workflow →
- Branch: 対象ブランチを選択
- 実行モード: ci_only / ci_then_cd / cd_only を選択
- Run workflow をクリック

#### デプロイのみ実行（cd_only）

```bash
# GitHub ActionsのワークフローをGitHub UIから手動実行
# Branch: feature/xxx または main
# 実行モード: cd_only
```

---

### PDFドキュメントの管理

#### PDFファイルの追加手順

1. `src/backend/data/` に対象PDFを配置
2. compose環境: `docker compose restart backend`
3. WebUI（http://localhost/api/indexer）からインデックス化を実行

#### PDFのインデックス化（APIから）

```bash
# インデックス化
curl -X POST http://localhost:8000/api/pdf/index \
  -H "Content-Type: application/json" \
  -d '{"filename": "対象ファイル名.pdf"}'

# ステータス確認
curl "http://localhost:8000/api/pdf/status?filename=対象ファイル名.pdf"

# 削除
curl -X DELETE http://localhost:8000/api/pdf/delete \
  -H "Content-Type: application/json" \
  -d '{"document_id": "対象ファイル名（拡張子なし）"}'
```

---

### 状態確認

#### Podの状態確認

```bash
kubectl get pods -n aichat
kubectl get pods -n argocd
kubectl get pods -n istio-system
```

#### mTLSの状態確認

```bash
kubectl get peerauthentication -n aichat
```

#### サービスの状態確認

```bash
kubectl get svc -n aichat
```

#### ChromaDB接続確認

```bash
kubectl exec -it $(kubectl get pod -n aichat -l app=backend -o jsonpath='{.items[0].metadata.name}') \
  -n aichat -c fastapi-app -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://vectordb-service:8000/api/v2/heartbeat').status)"
# → 200
```

#### ログの確認

```bash
# backendのログ
kubectl logs -f deploy/backend -n aichat -c fastapi-app

# vectordbのログ
kubectl logs -f deploy/vectordb -n aichat

# docker composeモードのログ
docker compose logs -f backend
```

---

### 障害対応

#### Podが起動しない場合

```bash
kubectl describe pod <pod名> -n aichat
kubectl rollout restart deployment/backend -n aichat
```

#### ChromaDBに接続できない場合

```bash
kubectl rollout restart deployment/vectordb -n aichat
```

#### docker composeでDockerに接続できない場合

```bash
# Docker PATHが通っていない場合
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Minikubeモードのままになっている場合
eval $(minikube docker-env -u)
docker compose up -d
```

#### CIが実行されない（待機中のまま）

```bash
# Runnerが起動しているか確認
ps aux | grep Runner.Listener | grep -v grep

# Runnerを再起動
kill -9 $(pgrep -f Runner.Listener)
cd ~/git_lesson/ai_chat/actions-runner
./run.sh &
```

---

### システムの停止

```bash
# docker composeモード
docker compose down

# Minikubeモード
minikube stop
```

---

### 一時的な外部公開（ユーザーレビュー用）

```bash
# ngrokで外部公開（compose環境のみ・社内機密に注意）
ngrok http 80
```

> ⚠️ ngrokはcompose環境でのユーザーレビュー時のみ使用。社内機密情報の取り扱いに注意。

---

### システム起動（Minikubeモード・HTTP）

```bash
./switch_to_minikube.sh
./switch_to_http.sh
# ドキュメントビューア: http://localhost:8090/api/specs
# バックエンド API:     http://localhost:8090/swagger/docs
# PDFインデクサー:      http://localhost:8090/api/indexer
```

### システム起動（Minikubeモード・HTTPS）

```bash
./switch_to_minikube.sh
./switch_to_https.sh
# ドキュメントビューア: https://localhost/api/specs
# バックエンド API:     https://localhost/swagger/docs
# PDFインデクサー:      https://localhost/api/indexer
```
