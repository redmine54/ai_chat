# 2. 各環境でのGitLab運用ポイント
<div align="right">最終更新日: 2026-06-07</div>

### compose環境

- **ブランチ戦略**：`feature/*` ブランチで開発し、`develop` へマージ
- **CI**：GitLab CI でDockerビルド・ユニットテスト・統合テストを自動実行
- **MRルール**：セルフマージ禁止、最低1名レビュー必須
- **禁止事項**：`.env` ファイル・APIキー・パスワードのコミット禁止（`.gitignore` で強制）
- **GitLab Secrets**：CI変数（`CI/CD → Variables`）でAPIキーを管理し、Masked設定必須

### minikube環境

- **ブランチ**：`develop` ブランチのCI上でk8sマニフェスト検証（`kubectl apply --dry-run`）を追加
- **マニフェスト管理**：k8s/overlays/minikube を GitLab で管理
- **Secrets管理**：k8s Secretsはマニフェストに含めず、CI変数から `kubectl create secret` で投入

### staging環境

- **ブランチ**：`develop` → `staging` へのマージをトリガーにデプロイ
- **承認フロー**：staging へのMRはリードエンジニア承認必須（Protected Branch + Approvals設定）
- **ArgoCD連携**：GitLab CIがAKSのArgoCDに同期指示、自動デプロイ
- **Secrets**：Azure Key Vault + External Secrets Operator でk8s Secretsを注入（GitLabには保存しない）
- **ITGC対応**：MR承認記録・デプロイログをGitLabで証跡として保持

### product環境

- **ブランチ**：`staging` → `main` へのマージをトリガーにデプロイ
- **承認フロー**：MRはPM + セキュリティ担当の2名承認必須
- **Protected Branch**：`main` への直接pushを完全禁止
- **デプロイ制限**：手動トリガー（`when: manual`）＋承認者のみ実行可能
- **タグ管理**：`v*` タグ付きコミットのみデプロイ可能に制限
- **監査ログ**：GitLab Audit Eventsを有効化し、全操作を記録
