# Architecture Design

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

| 環境 | 基盤 | 用途 |
|------|------|------|
| 開発 | docker compose | ローカル開発・デバッグ |
| 検証 | Minikube | K8s・mTLS動作確認 |
| 本番 | AKS（Azure） | 社内サービス提供 |

---

### CI/CDパイプライン

```
開発者がfeatureブランチにPush
        ↓
GitHub Actions（Self-hosted Runner）
  1. Dockerイメージビルド
  2. Unitテスト
  3. Integrationテスト
  4. K8sマニフェスト検証
        ↓ CI成功
Pull Request → mainへマージ
        ↓
ArgoCD（GitOps）
  → K8sへ自動デプロイ
```

---

### セキュリティアーキテクチャ

| レイヤー | 対策 | 実装 |
|---------|------|------|
| 外部通信 | HTTPS（TLS） | Istio Gateway + 証明書 |
| サービス間通信 | mTLS（STRICT） | Istio PeerAuthentication |
| 認証 | Azure AD連携 | 予定 |
| ネットワーク | 社内限定 | NetworkPolicy |
