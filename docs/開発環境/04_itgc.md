# 4. ITGC 4項目への対応
<div align="right">最終更新日: 2026-06-07</div>

## ① アクセス管理（Access to Programs and Data）

| 対応事項 | 実装方法 |
|---|---|
| 最小権限の原則 | RBAC（k8s / GitLab / Azure IAM）で役割ごとに権限を制限 |
| 本番アクセス制限 | product環境への開発者アクセス禁止、運用担当のみ許可 |
| 特権アカウント管理 | Azure PIM（Privileged Identity Management）で一時昇格・承認フロー |
| アクセスログ | GitLab Audit Events + Azure Monitor で全アクセスを記録 |
| 定期アクセスレビュー | 四半期ごとにGitLab / Azure IAMの権限棚卸し |

## ② 変更管理（Program Change）

| 対応事項 | 実装方法 |
|---|---|
| 変更申請 | Redmineのチケットで変更内容・影響範囲・テスト結果を記録 |
| コードレビュー | GitLab MRで必須レビュー・承認（stagingは1名、productは2名） |
| テスト証跡 | GitLab CI のパイプライン実行結果をテスト証跡として保持 |
| 本番変更制限 | `main`への直接pushを禁止、MR + 承認 + 手動トリガーのみ |
| 緊急変更手順 | Redmineに緊急変更チケットを起票し事後承認フローを整備 |

## ③ コンピュータ運用管理（Computer Operations）

| 対応事項 | 実装方法 |
|---|---|
| デプロイ自動化 | ArgoCD + GitLab CI による自動デプロイで手動ミスを排除 |
| 監視・アラート | Azure Monitor + Prometheus / Grafana でシステム監視 |
| バックアップ | AzureマネージドDBの自動バックアップ + リストア手順書整備 |
| インシデント管理 | Redmineでインシデントチケット管理、対応記録を保持 |
| ジョブ管理 | バッチ処理の実行ログをAzure Monitor Logsに集約 |

## ④ 開発・導入管理（Systems Development and Maintenance）

| 対応事項 | 実装方法 |
|---|---|
| 環境分離 | compose / minikube / staging / product を完全分離 |
| 試験完了基準 | Redmineチケットで単体・組合せ・総合試験の合否を記録 |
| 本番移行承認 | `staging → main` MRのPM承認を移行承認の証跡とする |
| IaC管理 | Terraform で infrastructure をコード管理し変更履歴を保持 |
| ドキュメント管理 | 設計書・手順書をGitLabリポジトリで版管理 |
