# ai_chat
<div align="right">最終更新日: 2026-06-05</div>

社内向けRAG（Retrieval-Augmented Generation）+ LLMチャットシステム

---

## 概要

社内PDFドキュメントをベースにしたAIチャットシステムです。  
FastAPI + ChromaDB + Claude API（Anthropic）によるRAGアーキテクチャで、Istio mTLSによるセキュアな社内限定環境を提供します。

### 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Nginx（静的ファイル配信） |
| バックエンド | FastAPI（Python 3.12） |
| LLM | Gemini API（gemini-2.0-flash） |
| ベクトルDB | ChromaDB |
| コンテナオーケストレーション | Kubernetes（Minikube / AKS） |
| サービスメッシュ | Istio（mTLS） |
| GitOps / CD | ArgoCD |
| CI | GitHub Actions（Self-hosted Runner） |
| IaC | Terraform |

---

## アーキテクチャ

```
[ユーザー]
    │ HTTPS
    ▼
[Istio IngressGateway]  ← mTLS（サービス間通信を暗号化）
    │
    ├─► [Frontend: Nginx]          静的ファイル配信
    │
    └─► [Backend: FastAPI]         RAG処理・APIサーバー
              │
              ├─► [Claude API]     LLM（回答生成）
              │
              └─► [VectorDB: ChromaDB]  ベクトル検索
```

### RAGの処理フロー

1. PDFドキュメントからテキストを抽出
2. テキストをチャンク分割してChromaDBにベクトル保存
3. ユーザーの質問に対してChromaDBで類似文書を検索
4. 検索結果をコンテキストにClaude APIへ送信
5. Claudeが文書に基づいた回答を生成

---

## ディレクトリ構成

```
ai_chat/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI設定
├── actions-runner/                 # GitHub Actions Self-hosted Runner（Git管理外）
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── namespace.yaml
│   ├── kustomization.yaml
│   └── istio/
│       ├── gateway.yaml            # Istio Gateway設定
│       ├── peer-auth.yaml          # mTLS PeerAuthentication設定
│       ├── virtual-service.yaml    # VirtualService設定
│       └── certs/                  # TLS証明書
├── docs/                           # プロジェクトドキュメント
│   ├── design/                     # 設計書（アーキテクチャ・UI・シーケンス図等）
│   ├── requirements/               # 要件定義（機能・非機能・ユースケース）
│   ├── specifications/             # 仕様書（API・プログラム・エラーハンドリング）
│   └── operations/                 # 運用ドキュメント（runbook・インシデント対応）
├── k8s/
│   ├── base/                       # K8sマニフェスト（共通）
│   │   ├── backend.yaml
│   │   └── vectordb.yaml
│   └── overlays/
│       ├── minikube/               # Minikube環境用設定
│       └── aks/                    # AKS環境用設定
├── overlays/                       # Kustomizeオーバーレイ
├── security/                       # セキュリティ設定
├── src/
│   ├── backend/                    # FastAPIアプリ
│   │   ├── app/
│   │   │   ├── main.py             # FastAPIエントリーポイント
│   │   │   └── rag.py              # RAG処理（PDF取込・ベクトル検索・Claude呼出）
│   │   ├── templates/              # HTMLテンプレート（ドキュメントビューア）
│   │   ├── static/                 # 静的ファイル
│   │   ├── data/                   # 取り込み対象PDFドキュメント
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── frontend/                   # Nginxフロントエンド
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   └── vectordb/                   # ChromaDB設定
│       └── Dockerfile
├── terraform/                      # AKSインフラ設定
├── tests/
│   ├── unit/                       # ユニットテスト
│   ├── integration/                # 統合テスト
│   ├── e2e/                        # E2Eテスト
│   └── performance/                # パフォーマンステスト
├── docker-compose.yml              # ローカル開発用
├── copy_docs.sh                    # docsコピースクリプト
├── create_gatewaykey.sh            # Istio Gatewayキー生成
├── docs_setup.sh                   # ドキュメントセットアップ
├── generate_api_spec.sh            # API仕様書生成
├── generate_program_spec.sh        # プログラム仕様書生成
├── generate_repositories.sh        # リポジトリ生成
├── install_Istio_on_m1.sh          # Istioインストール（M1 Mac用）
├── minikube_start.sh               # Minikube起動（HTTP）
├── minikube_start_https.sh         # Minikube起動（HTTPS）
├── minikube_build.sh               # Dockerイメージビルド
├── minikube_build_https.sh         # Dockerイメージビルド（HTTPS）
├── overwrite_md_files.sh           # Markdownファイル上書き
├── switch_to_compose.sh            # docker composeモードに切り替え
├── switch_to_minikube.sh           # Minikubeモードに切り替え
├── switch_to_http.sh               # HTTPアクセスに切り替え
└── switch_to_https.sh              # HTTPSアクセスに切り替え
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
- GitHub CLI（`gh`）
- Anthropic APIキー（Claude API利用のため）

### Istioのインストール

```bash
./install_Istio_on_m1.sh
```

### GitHub Actions Self-hosted Runnerのセットアップ

1. GitHubリポジトリの `Settings → Actions → Runners → New self-hosted runner` を開く
2. 表示されるコマンドを実行してRunnerをインストール
3. Runnerを起動

```bash
cd actions-runner
./run.sh
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
| バックエンド API（Swagger） | http://localhost:8000/api/chat/uiswagger/docs |
| ドキュメントビューア | http://localhost:8000/api/chat/uiapi/specs |
| ChromaDB | http://localhost:8001 |

---

### Minikubeモード（HTTP）

```bash
./switch_to_minikube.sh
./switch_to_http.sh
```

アクセス: `http://localhost:8080`

---

### Minikubeモード（HTTPS + mTLS）

```bash
./switch_to_minikube.sh
./switch_to_https.sh
```

アクセス: `https://localhost`

---

## 環境切り替え

| コマンド | 用途 |
|---------|------|
| `./switch_to_compose.sh` | docker composeモードに切り替え |
| `./switch_to_minikube.sh` | Minikubeモードに切り替え |
| `./switch_to_http.sh` | HTTPアクセス（port-forward） |
| `./switch_to_https.sh` | HTTPSアクセス（minikube tunnel） |

---

## APIエンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| `POST` | `/api/chat` | チャット（RAG回答生成） |
| `GET` | `/api/specs` | ドキュメントビューア |
| `GET` | `/api/docs/*` | ドキュメント静的ファイル配信 |
| `GET` | `/swagger/docs` | Swagger UI |
| `GET` | `/swagger/redoc` | ReDoc UI |

### チャットAPIリクエスト例

```bash
curl -X POST http://localhost:8000/api/chat/uiapi/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "契約期間はいつまでですか？"}'
```

```json
{
  "answer": "契約書に基づき、契約期間は2026年6月1日から6月30日までです。"
}
```

---

## CI/CD

### CI（GitHub Actions）

Self-hosted Runnerを使用し、featureブランチへのpush時に自動実行されます。

| ステップ | 内容 |
|---------|------|
| Dockerイメージビルド | `docker build` |
| Unitテスト | `pytest tests/unit/` |
| Integrationテスト | `pytest tests/integration/` |
| K8sマニフェスト検証 | `kubectl apply --dry-run`（minikube/aksモード時） |

`ci.yml` の `DEPLOY_ENV` 変数で動作を切り替えます：

| 値 | 内容 |
|----|------|
| `compose` | K8s検証をスキップ |
| `minikube` | Minikubeでマニフェスト検証 |
| `aks` | AKSでマニフェスト検証 |

### CD（ArgoCD）

ArgoCDがGitリポジトリの変更を検知して自動デプロイします。

```bash
# ArgoCDの状態確認
kubectl get pods -n argocd
```

---

## セキュリティ

### mTLS（サービス間通信）

IstioのPeerAuthenticationによりサービス間通信をSTRICTモードで暗号化します。

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

### APIキー管理

Claude APIキーはKubernetes Secretとして管理し、環境変数経由でバックエンドに渡します。ソースコードへの直接記載は禁止します。

---

## 一時的な外部公開（デモ用）

```bash
# ngrokで一時的に外部公開
ngrok http 8000
```

> ⚠️ 社内機密情報を含むためデモ目的のみで使用してください。使用後は必ずngrokを停止してください。

---

## リリース管理

```bash
# タグの作成とプッシュ
git tag v0.1.0
git push origin v0.1.0
```

| バージョン | 内容 |
|-----------|------|
| v0.1.0 | 初期リリース（RAG基盤・CI/CD・mTLS） |

---

## ドキュメント

プロジェクトの詳細ドキュメントは [docs/README.md](docs/README.md) を参照してください。

| カテゴリ | パス |
|---------|------|
| 概要 | [docs/overview/](docs/overview/) |
| 要件定義 | [docs/requirements/](docs/requirements/) |
| 設計書 | [docs/design/](docs/design/) |
| 仕様書 | [docs/specifications/](docs/specifications/) |
| データ設計 | [docs/data/](docs/data/) |
| 運用ドキュメント | [docs/operations/](docs/operations/) |
| テスト | [docs/testing/](docs/testing/) |
| 開発環境設計規定 | [docs/開発環境/](docs/開発環境/) |

ドキュメントビューア（起動後）: `http://localhost:8000/api/chat/uiapi/specs`

---

## ライセンス

[LICENSE](LICENSE)
