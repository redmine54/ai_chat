# Glossary

## 用語集

| 用語 | 説明 |
|------|------|
| RAG | Retrieval-Augmented Generation。外部ドキュメントを検索して回答を生成するAI手法 |
| LLM | Large Language Model。大規模言語モデル（例：GPT-4、Claude） |
| ベクトル検索 | テキストを数値ベクトルに変換して意味的な類似度で検索する手法 |
| ChromaDB | OSSのベクトルデータベース。埋め込みベクトルの保存・検索に使用 |
| FastAPI | PythonのWebフレームワーク。高速なAPI開発が可能 |
| Kubernetes（K8s） | コンテナオーケストレーションプラットフォーム |
| Minikube | ローカル環境でKubernetesを動作させるツール |
| AKS | Azure Kubernetes Service。AzureのマネージドK8sサービス |
| Istio | Kubernetesのサービスメッシュ。mTLS・トラフィック管理を提供 |
| mTLS | Mutual TLS。双方向TLS認証によるサービス間通信の暗号化 |
| ArgoCD | GitOpsベースのCDツール。Gitリポジトリの変更を自動デプロイ |
| GitOps | Gitリポジトリを単一の真実のソースとして使用するCI/CDの手法 |
| Self-hosted Runner | GitHub Actionsをローカル環境で実行するためのエージェント |
| Kustomize | K8sマニフェストを環境ごとにカスタマイズするツール |
| Terraform | インフラをコードで管理するIaCツール |
| IngressGateway | Istioの外部トラフィック受け付けコンポーネント |
| VirtualService | Istioのトラフィックルーティング設定リソース |
| PeerAuthentication | IstioのmTLS設定リソース |
| Namespace | K8sのリソース分離単位。本システムでは`aichat`を使用 |
| Pod | K8sの最小デプロイ単位。1つ以上のコンテナで構成 |
| Sidecar | Istioが自動注入するプロキシコンテナ（envoy） |
| Embedding | テキストをベクトルに変換する処理 |
| Chunk | PDFドキュメントを分割した単位 |
| docker compose | 複数コンテナをローカルで管理するツール（開発環境用） |
