# System Overview

## システム概要

社内PDFドキュメントを知識ベースとしたRAG（Retrieval-Augmented Generation）+LLMチャットシステムです。社内ネットワーク内でのみ動作するセキュアな構成を採用しています。

## システム構成図

```
社内ユーザー（ブラウザ）
        ↓ HTTPS
Istio IngressGateway
        ↓ mTLS
    ┌───────────────────────────────┐
    │  Kubernetes Cluster（aichat） │
    │                               │
    │  ┌─────────┐  ┌───────────┐  │
    │  │ Frontend │  │  Backend  │  │
    │  │ (Nginx)  │→ │ (FastAPI) │  │
    │  └─────────┘  └─────┬─────┘  │
    │                     ↓ mTLS   │
    │               ┌───────────┐  │
    │               │  VectorDB │  │
    │               │ (ChromaDB)│  │
    │               └───────────┘  │
    └───────────────────────────────┘
```

## コンポーネント

| コンポーネント | 技術 | 役割 |
|--------------|------|------|
| フロントエンド | Nginx | チャットUI提供 |
| バックエンド | FastAPI（Python 3.12） | RAG処理・LLM連携 |
| ベクトルDB | ChromaDB | PDFのベクトルデータ管理 |
| サービスメッシュ | Istio | mTLS・トラフィック管理 |
| コンテナ基盤 | Kubernetes（Minikube/AKS） | コンテナオーケストレーション |
| GitOps/CD | ArgoCD | 自動デプロイ管理 |
| CI | GitHub Actions | テスト・ビルド自動化 |
| IaC | Terraform | AKSインフラ管理 |

## RAG処理フロー

```
1. ユーザーが質問を入力
        ↓
2. バックエンドが質問をベクトル化
        ↓
3. ChromaDBから関連ドキュメントを検索
        ↓
4. 関連ドキュメント＋質問をLLMに送信
        ↓
5. LLMが回答を生成
        ↓
6. ユーザーに回答を返却
```

## 環境構成

| 環境 | 用途 | 基盤 |
|------|------|------|
| 開発 | ローカル開発・デバッグ | docker compose |
| 検証 | K8s動作確認・mTLS検証 | Minikube |
| 本番 | 社内サービス提供 | AKS（Azure） |

## セキュリティ

| 対策 | 内容 |
|------|------|
| mTLS | サービス間通信の暗号化（Istio） |
| HTTPS | 外部通信の暗号化（Istio Gateway） |
| 社内限定 | 社内ネットワーク内でのみ動作 |
| 認証 | Azure AD連携（予定） |
