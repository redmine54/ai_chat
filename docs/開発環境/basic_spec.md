# 基本仕様
<div align="right">最終更新日: 2026-06-07</div>

k8s / IaC / GitLabを使用したIaC・CI/CD・RBAC・マイクロサービス開発環境の設計方針

---

| 項目 | 内容 |
|---|---|
| インフラ | k8s / AKS / IaC（Terraform） |
| CI/CD | GitLab CI/CD |
| 認可 | RBAC |
| 構成管理 | GitLab（社内LAN接続） |
| プロジェクト管理 | Redmine |
| ネットワーク | 社内LAN + Azure閉域網 |
| 外部公開 | ngrok（compose環境・単体試験時のみ） |

| 環境 | 基盤 | 用途 |
|---|---|---|
| compose環境 | docker compose / ローカルPC | 開発・単体試験・ユーザーレビュー（ngrok） |
| minikube環境 | Minikube / ローカルPC | composeで不可なk8s試験 |
| staging環境 | AKS | 組合せ試験・ITGC確認 |
| product環境 | AKS | 総合試験・本番運用・ITGC確認 |

| セキュリティ原則 | 内容 |
|---|---|
| secrets分離 | パスワード・APIキーは環境ごとに分離 |
| DB分離 | 環境ごとにDBを分離 |
| GitLab登録禁止 | secrets・本番データのGitLab登録禁止 |
| 本番データ禁止 | 開発環境での本番データ使用禁止 |
