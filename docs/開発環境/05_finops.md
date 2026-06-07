# 5. FinOps 運用推奨内容
<div align="right">最終更新日: 2026-06-07</div>

## staging環境

| カテゴリ | 推奨内容 | ツール・方法 |
|---|---|---|
| **コスト可視化** | 環境タグ（`env=staging`）を全リソースに付与しコストを分離集計 | Azure Cost Management + タグポリシー |
| **ノードスケール** | 試験時間帯のみクラスター起動、夜間・週末は自動停止 | AKS Start/Stop スケジュール（Azure Automation） |
| **オートスケール** | 負荷試験時のみHPA/VPAを有効化、平常時はレプリカ数を最小化 | HPA / VPA / KEDA |
| **ノードプール最適化** | Spot VMを活用しノードコストを削減（試験用途のため中断許容） | AKS Spot Node Pool |
| **不要リソース削除** | 試験完了後に一時リソース（LoadBalancer・PVC等）を即時削除 | GitLab CIのクリーンアップジョブ |
| **コスト予算アラート** | 月次予算を設定し80%・100%到達時にアラート通知 | Azure Budgets + Action Group |
| **DBコスト最適化** | 試験用DBは最小SKUを使用、試験外は一時停止 | Azure Database 一時停止機能 |
| **コンテナリソース制限** | requests/limitsを適切に設定しノードの過剰プロビジョニングを防止 | k8s ResourceQuota / LimitRange |

## product環境

| カテゴリ | 推奨内容 | ツール・方法 |
|---|---|---|
| **コスト可視化** | サービス・チームごとにタグを付与し部門別コストを集計 | Azure Cost Management + タグポリシー |
| **Reserved Instances** | 常時稼働リソース（DBサーバー等）は1〜3年予約でコスト最大72%削減 | Azure Reserved VM Instances |
| **オートスケール** | トラフィックに応じてPod・Nodeを自動スケールし過剰リソースを排除 | HPA / Cluster Autoscaler / KEDA |
| **ノードプール最適化** | ベースロードはオンデマンドVM、スパイク対応はSpot VMで対処 | AKS System/User Node Pool分離 |
| **コンテナリソース適正化** | 定期的にリソース使用率を分析しrequests/limitsを見直し | Azure Monitor + Vertical Pod Autoscaler |
| **ストレージ最適化** | アクセス頻度に応じてストレージTierを自動移行（Hot→Cool→Archive） | Azure Blob Storage ライフサイクルポリシー |
| **コスト予算管理** | 月次・四半期予算を設定し超過時は自動アラート＋担当者通知 | Azure Budgets + Cost Anomaly Alerts |
| **FinOpsレビュー** | 月次でコスト分析レポートを作成し最適化アクションを記録 | Azure Cost Management レポート |
| **不要リソース棚卸し** | 月次で未使用リソース（孤立ディスク・IP等）を検出・削除 | Azure Advisor + 自動クリーンアップスクリプト |
| **egress最適化** | Azure Private Endpoint活用でインターネットegressコストを削減 | Private Endpoint / Private Link |
