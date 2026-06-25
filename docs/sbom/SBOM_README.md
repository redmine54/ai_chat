# SBOM管理ガイド

> **Software Bill of Materials（ソフトウェア部品表）**の自動生成・脆弱性スキャン・ライセンスコンプライアンス・K8s連携を GitHub Actions CI/CD に組み込む統合ガイドです。

---

## 概要

SBOM（Software Bill of Materials）とは、ソフトウェアを構成するすべてのコンポーネント・ライブラリ・依存関係を記録した「部品表」です。製造業における部品表と同様に、ソフトウェアの透明性・安全性・追跡可能性を保証します。

### なぜSBOMが必要か

- **脆弱性の早期検知** — Log4Shell・SolarWinds などのサプライチェーン攻撃は、依存ライブラリ経由で感染します。SBOMにより依存関係を可視化し、CVE公開時に即座に影響範囲を特定できます。
- **ライセンスコンプライアンス** — OSS ライセンス違反（GPL汚染など）はビジネスリスクに直結します。SBOMで全ライセンスを自動チェックします。
- **監査・規制対応** — 米国大統領令 EO14028、EU サイバーレジリエンス法（CRA）など、SBOMの提出・開示を求める規制が世界的に拡大しています。
- **サプライチェーンの信頼性** — コンテナイメージへの署名・アテステーションにより、ビルド成果物の改ざんを検証可能にします。

---

## 対応スタック

| カテゴリ | 対応内容 |
|---------|---------|
| 言語 | Python、Node.js / JavaScript |
| コンテナ | Docker（マルチステージビルド対応）|
| オーケストレーション | Kubernetes + Helm チャート |
| CI/CD | GitHub Actions（セルフホストRunner対応）|
| ネットワーク | インターネット接続環境 / 社内閉域環境（プロキシ経由）両対応 |

---

## アーキテクチャ

```
コードプッシュ / PRオープン / リリース / 定期実行（毎日）
                    │
                    ▼
        ┌─────────────────────┐
        │   1. SBOM 生成      │  Syft（CycloneDX JSON）
        │   ─────────────     │  • Python依存（requirements.txt）
        │   対象スコープ      │  • Node.js依存（package-lock.json）
        │                     │  • Dockerイメージ層（OSパッケージ含む）
        │                     │  • Helmチャート依存関係
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐    ┌──────────────────┐
│ 2. 脆弱性    │    │ 3. ライセンス    │
│    スキャン   │    │    チェック      │
│              │    │                  │
│ Grype        │    │ pip-licenses     │
│ CVE照合      │    │ license-checker  │
│ SARIF出力    │    │ 許可/禁止リスト  │
└──────┬───────┘    └────────┬─────────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │ 4. K8s セキュリティ  │
        │                     │
        │ • マニフェスト検査   │  trivy config / kubesec
        │ • Helm依存スキャン   │  helm dependency + Syft
        │ • 実行中Pod SBOM    │  kubectl + Syft
        └──────────┬──────────┘
                   │
                   ▼ （release 時のみ）
        ┌─────────────────────┐
        │ 5. SBOM 署名        │  Cosign（キーレス / 社内CA）
        │                     │  Sigstore または 社内Rekor
        └─────────────────────┘
```

---

## 使用ツール

| ツール | 役割 | ライセンス |
|--------|------|-----------|
| [Syft](https://github.com/anchore/syft) | SBOM生成（CycloneDX/SPDX対応）| Apache-2.0 |
| [Grype](https://github.com/anchore/grype) | 脆弱性スキャン（CVE検出）| Apache-2.0 |
| [Cosign](https://github.com/sigstore/cosign) | SBOM署名・検証 | Apache-2.0 |
| [pip-licenses](https://github.com/raimon49/pip-licenses) | Pythonライセンス確認 | MIT |
| [license-checker](https://github.com/davglass/license-checker) | Node.jsライセンス確認 | BSD-3-Clause |
| [trivy](https://github.com/aquasecurity/trivy) | K8sマニフェスト検査 | Apache-2.0 |
| [kubesec](https://github.com/controlplaneio/kubesec) | K8sセキュリティスコアリング | Apache-2.0 |

---

## クイックスタート

### 1. ファイルを配置する

```
.github/
  workflows/
    sbom.yml              ← CIワークフロー本体
scripts/
  check_licenses.py       ← Pythonライセンスチェック
sbom-policy/
  policy.yml              ← ライセンス・脆弱性ポリシー設定
```

### 2. GitHub Actions の権限設定

**Settings → Actions → General** で以下を有効化：

- `Read and write permissions`
- `Allow GitHub Actions to create and approve pull requests`

### 3. GitHub Advanced Security の有効化

SARIF形式の脆弱性レポートをGitHub Security タブに表示するために必要です。

- Public リポジトリ：自動で有効
- Private リポジトリ：**Settings → Security → Code security** から有効化（有料プランが必要）

### 4. ポリシーを設定する

`sbom-policy/policy.yml` を編集してプロジェクトのポリシーを設定します。

```yaml
vulnerability:
  fail_on_severity: high      # critical | high | medium | low

license:
  denied:
    - GPL-2.0
    - GPL-3.0
    - AGPL-3.0
```

---

## 閉域環境（社内プロキシ / オフライン環境）での運用

閉域環境では追加の設定が必要です。詳細は技術者向け手順書を参照してください。

### 主要な対応点

**① ツールバイナリのミラーリング**

```bash
# 社内ファイルサーバーにバイナリを配置
# セルフホストRunnerのベースイメージへ事前インストールを推奨
```

**② 脆弱性DBのミラーリング（最重要）**

```bash
# 踏み台マシン（外部接続可能）で定期実行（週1回以上推奨）
grype db update
rsync -av ~/.cache/grype/db/ fileserver.internal.company.local:/share/grype-db/
```

ワークフロー側での設定：

```yaml
env:
  GRYPE_DB_CACHE_DIR: /mnt/shared/grype-db    # 社内共有ストレージ
  GRYPE_DB_AUTO_UPDATE: 'false'                # 外部自動更新を無効化
```

> ⚠️ **重要**: `GRYPE_DB_AUTO_UPDATE` を `false` にしないと、閉域環境でタイムアウトエラーになります。

**③ SBOM署名（社内Rekor使用）**

```yaml
env:
  REKOR_SERVER: ${{ secrets.INTERNAL_REKOR_URL }}
  SIGSTORE_ROOT_FILE: /etc/pki/internal-ca-bundle.pem
```

**④ セルフホストRunner の推奨**

GitHub-hosted Runner はインターネット経由でツールをダウンロードするため、閉域環境では使用困難です。セルフホストRunner のベースイメージにツール群を事前組み込むことで、ネットワーク依存を最小化できます。

```yaml
# ワークフローの runs-on を変更
jobs:
  generate-sbom:
    runs-on: [self-hosted, linux, sbom-capable]
```

---

## 生成される成果物

各 CI 実行で以下が自動生成・保存されます。

| 成果物 | 形式 | 保存先 | 保持期間 |
|-------|------|--------|---------|
| SBOM（アプリ依存） | CycloneDX JSON | GitHub Artifacts | 90日 |
| SBOM（イメージ全層） | CycloneDX JSON | GitHub Artifacts | 90日 |
| SBOM（Helm依存） | CycloneDX JSON | GitHub Artifacts | 90日 |
| 脆弱性レポート | SARIF | GitHub Security タブ | 無期限 |
| ライセンスレポート | Markdown | GitHub Artifacts | 90日 |
| SBOM署名・証明書 | .sig / .pem | GitHub Release | 無期限 |

---

## ライセンスポリシー

### 許可リスト（デフォルト）

- MIT、Apache-2.0、BSD-2-Clause / BSD-3-Clause
- ISC、PSF（Python Software Foundation License）
- MPL-2.0、LGPL-2.1 / LGPL-3.0

### 禁止リスト（デフォルト）

- GPL-2.0、GPL-3.0、AGPL-3.0
- SSPL、BUSL（Business Source License）

### 例外申請

禁止ライセンスのパッケージを使用する場合は、法務レビューの上 `sbom-policy/policy.yml` の `approved_exceptions` に理由・承認者・期限を記載してください。

```yaml
license:
  approved_exceptions:
    some-package:
      reason: "社内審査済み。本番環境では使用しない開発ツール。"
      ticket: "SEC-456"
      approved_by: "security-team"
      expires: "2026-03-31"
```

---

## K8s固有の機能

### Helmチャート依存スキャン

```bash
helm dependency update ./charts/myapp
syft dir:./charts --output cyclonedx-json=sbom-helm.json
```

### 実行中PodのSBOM（定期ジョブ）

```bash
kubectl get pods -n production -o json | \
  jq -r '.items[].spec.containers[].image' | \
  sort -u | while read image; do
    syft "${image}" --output cyclonedx-json
  done > runtime-sbom.json
```

### K8sマニフェスト検査

```bash
# trivy で設定ミス検出
trivy config ./k8s/ --format sarif --output k8s-config.sarif

# kubesec でセキュリティスコアリング
find k8s/ -name "*.yaml" | xargs -I{} kubesec scan {}
```

---

## トラブルシューティング

| 症状 | 原因 | 対処法 |
|------|------|--------|
| `database is too old` | 脆弱性DBミラーが未更新 | 踏み台からDB同期を実行 |
| `connection refused to anchore.io` | AUTO_UPDATEが有効 | `GRYPE_DB_AUTO_UPDATE=false` を設定 |
| `certificate not trusted` | 社内CA証明書未配布 | `SIGSTORE_ROOT_FILE` を社内CA PEM に設定 |
| `npm install failed` | 社内npmミラー未設定 | `.npmrc` でミラーURLを指定 |
| `kubesec: command not found` | Runnerにインストールなし | RunnerベースイメージへのSBOM |

---

## 定期メンテナンス

| 作業 | 推奨頻度 |
|------|---------|
| Grype脆弱性DBのミラー更新 | 週1回以上（cronで自動化推奨）|
| ツールバイナリの更新 | 月1回 |
| CVE除外設定の期限確認 | 四半期 |
| ライセンスポリシーのレビュー | 年1回（または法改正時）|

---

## ファイル構成

```
.github/
  workflows/
    sbom.yml                         # メインワークフロー
scripts/
  check_licenses.py                  # Pythonライセンスチェック
sbom-policy/
  policy.yml                         # ポリシー設定
SBOM_README.md                       # 本ドキュメント
```

---

## 参考リンク

- [Syft 公式ドキュメント](https://github.com/anchore/syft)
- [Grype 公式ドキュメント](https://github.com/anchore/grype)
- [Cosign / Sigstore 公式ドキュメント](https://github.com/sigstore/cosign)
- [NIST SP 800-218 (SSDF)](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [米国大統領令 EO14028](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
- [EU サイバーレジリエンス法（CRA）](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
- [経産省 SBOM 活用ガイダンス](https://www.meti.go.jp/policy/netsecurity/sbom.html)

---

## ライセンス

本リポジトリのワークフロー・スクリプトは MIT License の下で提供されます。
