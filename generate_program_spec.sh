#!/bin/bash

OUTPUT="docs/specifications/program_specification.md"

echo "Generating program_specification.md ..."

cat << 'EOF' > $OUTPUT
# Program Specification
対象モジュール名：
作成日：
作成者：
更新履歴：

---

## 1. 目的（Purpose）
本ドキュメントは、対象プログラムの処理仕様を定義し、開発・テスト・保守における共通理解を形成することを目的とする。

---

## 2. 前提条件（Prerequisites）
- 対象システム：
- 関連機能：
- 使用技術：
- 実行環境：
- 想定ユーザー：

---

## 3. 関連ドキュメント（Related Documents）
- System Overview
- Functional Requirements
- API Specification
- Data Model

---

## 4. 処理概要（Process Overview）
1.
2.
3.

---

## 5. 入出力仕様（I/O Specification）

### 5.1 入力（Input）
| 項目名 | 型 | 必須 | 説明 |
|--------|-----|------|------|

### 5.2 出力（Output）
| 項目名 | 型 | 説明 |
|--------|-----|------|

---

## 6. 詳細処理仕様（Detailed Logic）

### 6.1 処理ステップ
| Step | 処理内容 | 条件 | 備考 |
|------|-----------|--------|--------|

### 6.2 擬似コード（Pseudo Code）
\`\`\`
# pseudo code
\`\`\`

---

## 7. データ仕様（Data Specification）
- 使用テーブル：
- 主キー：
- 制約：

---

## 8. エラー処理（Error Handling）
| エラーコード | 発生条件 | メッセージ | 対応 |
|--------------|------------|-------------|--------|

---

## 9. ログ出力（Logging）
- ログレベル：
- 出力内容：

---

## 10. 性能要件（Performance Requirements）
- 最大処理件数：
- SLA：

---

## 11. セキュリティ要件（Security Requirements）
- 認証：
- 入力バリデーション：

---

## 12. テスト観点（Test Viewpoints）
- 正常系：
- 異常系：
- 境界値：

EOF

echo "program_specification.md generated."
