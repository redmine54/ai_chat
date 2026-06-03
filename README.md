# ai_chat

社内向けRAG（Retrieval-Augmented Generation）+ LLMチャットシステム

---

## 概要

社内PDFドキュメントをベースにしたAIチャットシステムです。  
FastAPI + ChromaDB + Istio mTLSによるセキュアな社内限定RAGシステムです。

### 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Nginx |
| バックエンド | FastAPI（Python 3.12） |
| ベクトルDB | ChromaDB |
| コンテナ orchestration | Kubernetes（Minikube / AKS） |
| サービスメッシュ | Istio（mTLS） |
| GitOps / CD | ArgoCD |
| CI | GitHub Actions（Self-hosted Runner） |
| IaC | Terraform |

---

## ディレクトリ構成

```
ai_chat/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI設定
├── base/
│   └── istio/
│       ├── gateway.yaml         # Istio Gateway設定
│       ├── peer-auth.yaml       # mTLS PeerAuthentication設定
│       └── virtual-service.yaml # VirtualService設定
├── docs/                        # ドキュメント
├── k8s/
│   ├── base/                    # K8sマニフェスト（共通）
│   └── overlays/
│       └── minikube/            # Minikube環境用設定
├── overlays/                    # 環境別設定
├── security/                    # セキュリティ設定
├── src/
│   ├── backend/                 # FastAPIアプリ
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── frontend/                # Nginxフロントエンド
├── terraform/                   # AKSインフラ設定
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── performance/
├── docker-compose.yml           # ローカル開発用
├── minikube_start.sh            # Minikube起動（HTTP）
├── minikube_start_https.sh      # Minikube起動（HTTPS）
├── minikube_build.sh            # Dockerイメージビルド
├── switch_to_compose.sh         # docker composeモードに切り替え
├── switch_to_minikube.sh        # Minikubeモードに切り替え
├── switch_to_http.sh            # HTTPアクセスに切り替え
└── switch_to_https.sh           # HTTPSアクセスに切り替え
```

---

## 環境セットアップ

### 前提条件

- Mac M1/M2/M3（ARM64）
- Docker Desktop
- Minikube
- kubectl
- Istio
- Helm

### Istioのインストール

```bash
./install_Istio_on_m1.sh
```

---

## 起動方法

### 開発モード（docker compose）

```bash
./switch_to_compose.sh
```

| サービス | URL |
|---------|-----|
| フロントエンド | http://localhost:80 |
| バックエンド API | http://localhost:8000/docs |
| ChromaDB | http://localhost:8001 |

---

### Minikubeモード（HTTP）

```bash
./switch_to_minikube.sh
./switch_to_http.sh
```

アクセス: `http://localhost:8080/docs`

---

### Minikubeモード（HTTPS + mTLS）

```bash
./switch_to_minikube.sh
./switch_to_https.sh
```

アクセス: `https://localhost/docs`

---

## CI/CD

### CI（GitHub Actions）

Self-hosted Runnerを使用します。

#### Self-hosted Runnerのセットアップ

1. GitHubリポジトリの `Settings → Actions → Runners → New self-hosted runner` を開く
2. 表示されるコマンドを実行してRunnerをインストール
3. Runnerを起動

```bash
cd actions-runner
./run.sh
```

#### CIの内容

| ステップ | 内容 |
|---------|------|
| Dockerイメージビルド | `docker build` |
| Unitテスト | `pytest tests/unit/` |
| Integrationテスト | `pytest tests/integration/` |
| K8sマニフェスト検証 | `kubectl apply --dry-run` |

### CD（ArgoCD）

ArgoCDがGitリポジトリの変更を検知して自動デプロイします。

```bash
# ArgoCDの状態確認
kubectl get pods -n argocd
```

---

## セキュリティ

### mTLS（サービス間通信）

IstioのPeerAuthenticationによりサービス間通信をSTRICTモードで暗号化しています。

```bash
# mTLS状態確認
kubectl get peerauthentication -n aichat
```

### HTTPS（外部通信）

Istio IngressGatewayによりHTTPS通信を終端します。

```bash
# 証明書の確認
kubectl get secret aichat-tls -n istio-system
```

---

## 環境切り替え

| コマンド | 用途 |
|---------|------|
| `./switch_to_compose.sh` | docker composeモード |
| `./switch_to_minikube.sh` | Minikubeモード |
| `./switch_to_http.sh` | HTTPアクセス（port-forward） |
| `./switch_to_https.sh` | HTTPSアクセス（minikube tunnel） |

---

## ライセンス

[LICENSE](LICENSE)
