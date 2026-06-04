# Runbook

## 運用手順書

### 日常運用

#### システム起動（Minikubeモード）

```bash
# HTTPモード
./switch_to_minikube.sh
./switch_to_http.sh
# アクセス: http://localhost:8080/docs

# HTTPSモード
./switch_to_minikube.sh
./switch_to_https.sh
# アクセス: https://localhost/docs
```

#### システム起動（docker composeモード）

```bash
./switch_to_compose.sh
# アクセス: http://localhost:8000/docs
```

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

# イメージ再ビルド
eval $(minikube docker-env)
docker build -t aichat:latest src/backend/
kubectl rollout restart deployment/backend -n aichat
```

#### ChromaDBに接続できない場合

```bash
# ChromaDB Podの確認
kubectl get pods -n aichat | grep vectordb

# ChromaDB再起動
kubectl rollout restart deployment/vectordb -n aichat

# 接続確認
kubectl exec -it <backend-pod名> -n aichat -c fastapi-app -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://vectordb-service:8000/api/v2/heartbeat').status)"
```

#### Minikubeが起動しない場合

```bash
# Minikubeの状態確認
minikube status

# Minikubeの再起動
minikube stop
minikube start
```

---

### メンテナンス

#### PDFドキュメントの追加

```bash
# APIでPDFをアップロード
curl -X POST https://localhost/api/v1/documents \
  -F "file=@/path/to/document.pdf"
```

#### システムの停止

```bash
# Minikubeモード
minikube stop

# docker composeモード
docker compose down
```
