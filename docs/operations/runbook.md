# Runbook
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-08</div>

## 運用手順書

### 日常運用

#### システム起動（docker composeモード）

```bash
./switch_to_compose.sh
```

| サービス | URL |
|---------|-----|
| フロントエンド | http://localhost:80 |
| バックエンド API（HTTP） | http://localhost:8000/swagger/docs |
| ドキュメントビューア（HTTP） | http://localhost:8000/api/specs |
| PDFインデクサー（HTTP） | http://localhost:8000/api/indexer |
| バックエンド API（HTTPS） | https://localhost/swagger/docs |
| ドキュメントビューア（HTTPS） | https://localhost/api/specs |
| PDFインデクサー（HTTPS） | https://localhost/api/indexer |
| ChromaDB | http://localhost:8001 |

#### システム起動（Minikubeモード・HTTP）

```bash
./switch_to_minikube.sh
./switch_to_http.sh
# ドキュメントビューア: http://localhost:8090/api/specs
# バックエンド API:     http://localhost:8090/swagger/docs
# PDFインデクサー:      http://localhost:8090/api/indexer
```

#### システム起動（Minikubeモード・HTTPS）

```bash
./switch_to_minikube.sh
./switch_to_https.sh
# ドキュメントビューア: https://localhost/api/specs
# バックエンド API:     https://localhost/swagger/docs
# PDFインデクサー:      https://localhost/api/indexer
```

#### システム起動（AKS環境）

| サービス | URL |
|---------|-----|
| ドキュメントビューア（HTTP） | http://localhost:8090/api/specs |
| バックエンド API（HTTP） | http://localhost:8090/swagger/docs |
| PDFインデクサー（HTTP） | http://localhost:8090/api/indexer |
| ドキュメントビューア（HTTPS） | https://localhost/api/specs |
| バックエンド API（HTTPS） | https://localhost/swagger/docs |
| PDFインデクサー（HTTPS） | https://localhost/api/indexer |

#### GitHub Actions Runner起動

```bash
cd actions-runner
./run.sh
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
```

---

### 障害対応

#### Podが起動しない場合

```bash
# Podの詳細確認
kubectl describe pod <pod名> -n aichat

# イメージ再ビルド（Minikubeモード）
eval $(minikube docker-env)
docker build -t aichat:latest -f src/backend/Dockerfile .
kubectl rollout restart deployment/backend -n aichat
```

#### ChromaDBに接続できない場合

```bash
# ChromaDB再起動
kubectl rollout restart deployment/vectordb -n aichat

# 接続確認
kubectl exec -it <backend-pod名> -n aichat -c fastapi-app -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://vectordb-service:8000/api/v2/heartbeat').status)"
```

#### Minikubeが起動しない場合

```bash
minikube status
minikube stop
minikube start
```

#### docker composeでDockerに接続できない場合

```bash
# Minikubeモードが残っている場合はリセット
eval $(minikube docker-env -u)
docker compose up -d
```

---

### メンテナンス

#### PDFドキュメントのインデックス化

```bash
# WebUIから実行
# http://localhost:8000/api/indexer

# APIから直接実行
curl -X POST http://localhost:8000/api/pdf/index \
  -H "Content-Type: application/json" \
  -d '{"filename": "対象ファイル名.pdf"}'
```

#### PDFファイルの追加手順

1. `src/backend/data/` に対象PDFを配置
2. compose環境: `docker compose restart backend`
3. minikube環境: `./rebuild_minikube.sh`
4. WebUI（/api/indexer）からインデックス化を実行

#### システムの停止

```bash
# Minikubeモード
minikube stop

# docker composeモード
docker compose down
```

#### 一時的な外部公開（デモ用）

```bash
# ngrokで外部公開（社内機密に注意）
ngrok http 8000
```
