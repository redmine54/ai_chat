# UI Design
<div align="right">作成日: 2026-06-05　最終更新日: 2026-06-08</div>

## UI設計

### 画面一覧

| 画面ID | 画面名 | URL | 概要 |
|--------|--------|-----|------|
| SCR-001 | チャット画面 | / または /api/chat/ui | RAG+Geminiチャットインターフェース |
| SCR-002 | PDFインデクサー画面 | /api/indexer | PDFのインデックス化・登録 |
| SCR-003 | 設定画面 | /settings | ユーザー設定（予定） |
| SCR-004 | ドキュメントビューア | /api/specs | プロジェクトドキュメント表示 |
| SCR-005 | APIドキュメント | /swagger/docs | Swagger UI |

---

### SCR-001: チャット画面（/）

```mermaid
graph TD
    subgraph SCR001[チャット画面]
        Header[ヘッダー: ai_chat　　PDFインデクサーボタン　ドキュメントボタン]
        subgraph History[チャット履歴エリア スクロール可能]
            Welcome[ウェルカムメッセージ\nこんにちは！何でも聞いてください。]
            AI1[AIバブル: Geminiが生成した回答]
            User1[ユーザーバブル: 入力した質問]
        end
        subgraph InputArea[入力エリア]
            Input[テキストエリア: Shift+Enterで改行・Enterで送信]
            SendBtn[送信ボタン]
        end
    end

    Header --> History
    History --> InputArea
```

**UI要素:**

| 要素 | 仕様 |
|------|------|
| チャット履歴 | スクロール可能・最新メッセージを下部に表示 |
| AIバブル | 左側表示・ロボットアイコン付き |
| ユーザーバブル | 右側表示・アクセントカラー背景 |
| ローディング | 3点ドットのバウンスアニメーション |
| 入力フォーム | 複数行入力対応・Enterで送信・Shift+Enterで改行 |
| 送信ボタン | 送信中は無効化 |
| ヘッダーリンク | PDFインデクサー・ドキュメントビューアへのナビゲーション |

---

### SCR-002: PDFインデクサー画面（/api/indexer）

```mermaid
graph TD
    subgraph SCR002[PDFインデクサー画面]
        Header2[ヘッダー: PDFインデクサー\ndata/配下のPDFをChromaDBにインデックス化]
        subgraph FileList[対象PDFファイル一覧]
            Reload[一覧を更新ボタン]
            PDF1[📄 業務委託契約書.pdf　　インデックス化ボタン　ステータスバッジ]
        end
        subgraph Log[実行ログ]
            LogArea[処理結果がリアルタイムで表示される]
        end
    end

    Header2 --> FileList
    FileList --> Log
```

**UI要素:**

| 要素 | 仕様 |
|------|------|
| PDFファイル一覧 | GET /api/pdf/listで取得・一覧を更新ボタンで再取得 |
| インデックス化ボタン | クリックでPOST /api/pdf/indexを実行 |
| ステータスバッジ | 処理中・完了（チャンク数）・エラーを色付きで表示 |
| 実行ログ | 処理開始・完了・エラーをリアルタイムで表示 |

---

### SCR-004: ドキュメントビューア（/api/specs）

```mermaid
graph LR
    subgraph Sidebar[左サイドバー]
        README[📄 README.md]
        M1[1. Overview]
        M2[2. Requirements]
        M3[3. Specifications]
        M4[4. Design]
        M5[5. Data]
        M6[6. Operations]
        M7[7. Testing]
    end

    subgraph Content[右コンテンツエリア]
        Title[# Project Title]
        Section[## 概要\n内容が表示されます...]
    end

    M1 -->|クリック| Content
    M2 -->|クリック| Content
    M3 -->|クリック| Content
    M4 -->|クリック| Content
```

---

### デザインガイドライン

| 項目 | 仕様 |
|------|------|
| フォント | -apple-system, BlinkMacSystemFont, Segoe UI（システムフォント） |
| カラー | プライマリ: #8fa89b（Muted Green）、背景: #faf8f5 |
| AIバブル | 背景: #f0ede9（サイドバーと同色） |
| ユーザーバブル | 背景: #8fa89b（アクセントカラー）、文字: 白 |
| レスポンシブ | PC・タブレット対応 |
| 言語 | 日本語 |
