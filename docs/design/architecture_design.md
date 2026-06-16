# Architecture Design
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-14</div>

## アーキテクチャ設計

### 全体構成

```mermaid
graph TD
    User([社内ユーザー]) -->|HTTPS TLS終端| IGW[Istio IngressGateway]
    Admin([管理者]) -->|HTTPS TLS終端| IGW
    IGW -->|mTLS STRICT| FE[Frontend\nNginx]
    IGW -->|mTLS STRICT| BE[Backend\nFastAPI]
    BE -->|mTLS| VDB[VectorDB\nChromaDB]
    BE -->|HTTPS| LLM[Gemini API\nGoogle]

    subgraph K8s[Kubernetes Cluster / Namespace: aichat]
        FE
        BE
        VDB
    end

    subgraph ArgoNS[Namespace: argocd]
        ARGO[ArgoCD\nGitOps CD]
    end

    subgraph IstioNS[Namespace: istio-system]
        ISTIO[Istio\nサービスメッシュ]
    end
```

---

### コンポーネント設計

#### Frontend（Nginx）

| 項目 | 内容 |
|------|------|
| イメージ | nginx:alpine |
| ポート | 80 |
| 役割 | 静的ファイル配信・リバースプロキシ |
| プロキシ先 | backend:8000 |

#### Backend（FastAPI）

| 項目 | 内容 |
|------|------|
| イメージ | ai_chat-backend:latest（カスタムビルド） |
| ポート | 8000 |
| 役割 | RAG処理・LLM連携・REST API提供・PDFインデックス化 |
| 環境変数 | CHROMA_HOST, CHROMA_PORT, GEMINI_API_KEY |
| エンドポイント | /health, /api/chat, /api/specs, /api/indexer, /api/pdf/list, /api/pdf/index, /api/pdf/status, /api/pdf/delete |

> ⚠️ `GEMINI_API_KEY` はソースコードに直接記載禁止。`.env` またはk8s Secret・GitHub Secretsで管理すること。

#### VectorDB（ChromaDB）

| 項目 | 内容 |
|------|------|
| イメージ | chromadb/chroma:latest |
| ポート | 8000（外部: 8001） |
| 役割 | ベクトルデータの保存・検索 |
| API | /api/v2 |
| 永続化 | PersistentVolume |

#### LLM（Gemini API）

| 項目 | 内容 |
|------|------|
| サービス | Google Gemini API |
| 埋め込みモデル | gemini-embedding-2 |
| 生成モデル | gemini-2.5-flash（デフォルト） |
| 役割 | PDFベクトル化・RAG回答生成 |
| 認証 | GEMINI_API_KEY（環境変数・GitHub Secrets） |

---

### 環境別構成

| 環境 | 基盤 | 用途 | 起動方法 |
|------|------|------|---------|
| 開発 | docker compose | ローカル開発・デバッグ・ユーザーレビュー | `./switch_to_compose.sh` |
| 検証（HTTP） | Minikube | K8s動作確認 | `./switch_to_minikube.sh && ./switch_to_http.sh` |
| 検証（HTTPS） | Minikube + Istio | mTLS動作確認 | `./switch_to_minikube.sh && ./switch_to_https.sh` |
| 本番 | AKS（Azure） | 社内サービス提供 | ArgoCD自動デプロイ |

---

### CI/CDパイプライン

```mermaid
flowchart TD
    A[開発者がfeatureブランチにPush] --> B[GitHub Actions\nSelf-hosted Runner on Mac M1]
    B --> C[フォーマット・Lint・型チェック]
    C --> D[Unitテスト・Integrationテスト\nカバレッジ計測]
    D --> E[Dockerイメージ脆弱性チェック\nTrivy]
    E --> F{DEPLOY_ENV}
    F -->|compose| G[K8s検証スキップ]
    F -->|minikube| H[minikubeでdry-run]
    F -->|aks| I[AKSでdry-run]
    G & H & I --> J[CI成功]
    J --> K[Pull Request → mainへマージ]
    K --> L[手動デプロイ\nworkflow_dispatch]
```

**workflow_dispatchの実行モード:**

| モード | 内容 |
|--------|------|
| ci_only | テストのみ（デフォルト・push時自動） |
| ci_then_cd | テスト完了後に自動デプロイ |
| cd_only | デプロイのみ（テストスキップ） |

---

### セキュリティアーキテクチャ

| レイヤー | 対策 | 実装 |
|---------|------|------|
| 外部通信 | HTTPS（TLS） | Istio Gateway + 自己署名証明書 |
| サービス間通信 | mTLS（STRICT） | Istio PeerAuthentication |
| APIキー管理 | 環境変数・Secrets管理 | .env / k8s Secret / GitHub Secrets / Azure Key Vault |
| 認証 | Azure AD連携 | 予定 |
| ネットワーク | 社内限定 | NetworkPolicy |
| 脆弱性チェック | コンテナイメージスキャン | Trivy（CI自動実行・.trivyignoreで管理） |

---

### Istio設定

| リソース | ファイル | 内容 |
|---------|---------|------|
| Gateway | base/istio/gateway.yaml | 外部HTTPSトラフィック受付 |
| PeerAuthentication | base/istio/peer-auth.yaml | mTLS STRICT設定 |
| VirtualService | base/istio/virtual-service.yaml | トラフィックルーティング |
| DestinationRule | base/istio/destination-rule.yaml | mTLS ISTIO_MUTUAL設定 |
