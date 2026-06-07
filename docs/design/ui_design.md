# UI Design
<div align="right">作成日: 2026-06-05</div>

## UI設計

### 画面一覧

| 画面ID | 画面名 | URL | 概要 |
|--------|--------|-----|------|
| SCR-001 | チャット画面 | / | メインのチャットインターフェース |
| SCR-002 | ドキュメント管理画面 | /admin | PDFのアップロード・削除 |
| SCR-003 | 設定画面 | /settings | ユーザー設定 |
| SCR-004 | ドキュメントビューア | /specs | プロジェクトドキュメント表示 |
| SCR-005 | APIドキュメント | /docs | Swagger UI |

---

### SCR-001: チャット画面

```mermaid
graph TD
    subgraph SCR001[チャット画面]
        Header[ヘッダー: ai_chat　　　　　　設定ボタン]
        subgraph History[チャット履歴エリア スクロール可能]
            AI1[AI: こんにちは！何でも聞いてください。]
            User1[ユーザー: 〇〇について教えてください]
            AI2[AI: 〇〇については...\n参照: document.pdf p.3]
        end
        Input[質問を入力...　　　　　　　　　　送信ボタン]
    end

    Header --> History
    History --> Input
```

**UI要素:**

| 要素 | 仕様 |
|------|------|
| チャット履歴 | スクロール可能・最新メッセージを下部に表示 |
| 入力フォーム | 複数行入力対応・Enterで送信 |
| 送信ボタン | 入力中はローディング表示 |
| 参照ドキュメント | クリックでドキュメント名・ページ数を表示 |

---

### SCR-002: ドキュメント管理画面

```mermaid
graph TD
    subgraph SCR002[ドキュメント管理画面]
        Upload[PDFをアップロードボタン]
        subgraph List[登録済みドキュメント一覧]
            Doc1[📄 manual.pdf　　削除ボタン]
            Doc2[📄 規程集.pdf　　削除ボタン]
            Doc3[📄 仕様書.pdf　　削除ボタン]
        end
    end

    Upload --> List
```

---

### SCR-004: ドキュメントビューア（/specs）

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
| フォント | Noto Sans JP（日本語対応） |
| カラー | プライマリ: #1976D2、背景: #F5F5F5 |
| ドキュメントビューア | ダークテーマ（背景: #0f1117） |
| レスポンシブ | PC・タブレット対応 |
| 言語 | 日本語 |
