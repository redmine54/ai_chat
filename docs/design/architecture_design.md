# Architecture Design
<div align="right">作成日: 2026-06-05</div>

## アーキテクチャ設計

### 全体構成

```
社内ユーザー
    ↓ HTTPS（TLS終端）
Istio IngressGateway
    ↓ mTLS（STRICT）
┌────────────────────────────────────────┐
│  Kubernetes Cluster                    │
│  Namespace: aichat                     │
│                                        │
│  ┌──────────┐    ┌──────────────────┐  │
│  │ Frontend │───▶│    Backend       │  │
│  │ (Nginx)  │    │   (FastAPI)      │  │
│  └──────────┘    └────────┬─────────┘  │
│                           │ mTLS       │
│                  ┌────────▼─────────┐  │
│                  │    VectorDB      │  │
│                  │   (ChromaDB)     │  │
│                  └──────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Namespace: argocd               │  │
│  │  ArgoCD（GitOps CD）             │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Namespace: istio-system         │  │
│  │  Istio（サービスメッシュ）        │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

### コンポーネント設計

#### Frontend（Nginx）

| 項目 | 内容 |
|------|------|
| イメージ | nginx:alpine |
| ポート | 80 |
| 役割 | 静的ファイル配信・リバースプロキシ |

#### Backend（FastAPI）

| 項目 | 内容 |
|------|------|
| イメージ | aichat:latest（カスタムビルド） |
| ポート | 8000 |
| 役割 | RAG処理・LLM連携・REST API提供 |
| 環境変数 | CHROMA_HOST, CHROMA_PORT |
| エンドポイント | /api/chat, /specs, /docs |

#### VectorDB（ChromaDB）

| 項目 | 内容 |
|------|------|
| イメージ | chromadb/chroma:latest |
| ポート | 8000 |
| 役割 | ベクトルデータの保存・検索 |
| API | /api/v2 |
| 永続化 | PersistentVolume |

---

### 環境別構成

| 環境 | 基盤 | 用途 | 起動方法 |
|------|------|------|---------|
| 開発 | docker compose | ローカル開発・デバッグ | `./switch_to_compose.sh` |
| 検証（HTTP） | Minikube | K8s動作確認 | `./switch_to_minikube.sh && ./switch_to_http.sh` |
| 検証（HTTPS） | Minikube + Istio | mTLS動作確認 | `./switch_to_minikube.sh && ./switch_to_https.sh` |
| 本番 | AKS（Azure） | 社内サービス提供 | ArgoCD自動デプロイ |

---

### CI/CDパイプライン

```
開発者がfeatureブランチにPush
        ↓
GitHub Actions（Self-hosted Runner on Mac M1）
  DEPLOY_ENV=compose  → K8s検証スキップ
  DEPLOY_ENV=minikube → minikubeでdry-run
  DEPLOY_ENV=aks      → AKSでdry-run
        ↓ CI成功
Pull Request → mainへマージ
        ↓
ArgoCD（GitOps）
  → K8sへ自動デプロイ
        ↓
タグ作成 → GitHubリリース
```

---

### セキュリティアーキテクチャ

| レイヤー | 対策 | 実装 |
|---------|------|------|
| 外部通信 | HTTPS（TLS） | Istio Gateway + 自己署名証明書 |
| サービス間通信 | mTLS（STRICT） | Istio PeerAuthentication |
| 認証 | Azure AD連携 | 予定 |
| ネットワーク | 社内限定 | NetworkPolicy |

---

### Istio設定

| リソース | ファイル | 内容 |
|---------|---------|------|
| Gateway | base/istio/gateway.yaml | 外部HTTPSトラフィック受付 |
| PeerAuthentication | base/istio/peer-auth.yaml | mTLS STRICT設定 |
| VirtualService | base/istio/virtual-service.yaml | トラフィックルーティング |
