# AI会社 - システム指示書

## 基本方針
- すべての出力・ログ・ドキュメントは日本語で記述すること
- 各エージェントはモジュール型プラグインとして独立して動作すること
- Discord向けの出力はMarkdown形式で適切にフォーマットすること

---

## ストレージ設計（重要）

### 2つのストレージを用途で使い分ける

| ストレージ | 用途 | 書き込み可否 |
|---|---|---|
| **Obsidian Vault** `ai company/` フォルダのみ | ナレッジベース（知識・情報） | 読み書き両方 |
| **Obsidian Vault** それ以外のフォルダ | CEOの個人知的財産 | **読み取りのみ・絶対に書き換えない** |
| **GitHub**（AI_companyリポジトリ） | システムファイル・ログ | 読み書き両方 |

---

## Obsidian Vault（ナレッジベース）

**Google Drive フォルダID**: `1DbXDxY9Hif_1LlASrUmm7JLcMe2pPReC`
（Google Drive MCP経由でアクセス。サーバー名: gdrive）

### ⚠️ Vault 操作の絶対ルール

> **Vault内の `ai company/` フォルダ以外は絶対に編集・削除・上書きしない。**
> CEOの個人ノート・知的財産が含まれており、許可なく変更することは禁止。

### エージェントが操作できる場所
```
[Vault]/ai company/        ← ここだけ読み書き可
    ├── ideas/
    ├── research/
    ├── clients/
    └── projects/
```

### エージェントが操作できない場所
```
[Vault]/ai company/ 以外のすべてのフォルダ・ファイル  ← 読み取りのみ・編集禁止
```

### ノート作成ルール
1. ノートはMarkdown形式で保存する
2. ファイル先頭にFrontmatterを必ず記述する（title / 作成日 / 更新日 / 作成者 / tags / status）
3. 関連ノートは `[[ノート名]]` リンクで相互参照する
4. 更新時は `更新日` フィールドを書き換え、内容は上書きせず追記する
5. テンプレートは `vault_schema/_templates/` を参照する

---

## GitHub（AI_companyリポジトリ）

**URL**: https://github.com/Masanobu0328/AI_company

### 保存するもの
- `agents/` — エージェント定義（claude.md / skills.md）
- `workflows/` — 業務フロー定義
- `logs/` — 全エージェントの活動ログ
- `dashboard/` — CEOダッシュボード
- `vault_schema/` — Obsidian Vaultの構造定義・テンプレート（参照用）

### ルール
1. ナレッジ（アイデア・クライアント情報・リサーチ）は保存しない
2. ログは `logs/sessions/[カテゴリ]/YYYY-MM-DD_[種別]_[概要].md` で記録する
3. 重要な変更はコミットメッセージに日本語で記述する

---

## エージェント呼び出しルール
- タスク依頼は必ずPM（プロジェクトマネージャー）を通すこと
- 緊急事項はSecretaryに直接連絡
- すべてのアウトプットは `logs/` に記録すること

---

## 拡張ルール
新しいエージェントを追加する場合：
1. `agents/<エージェント名>/` フォルダを作成（GitHub）
2. `claude.md`（役割・指示）と`skills.md`（能力定義）を作成
3. `README.md`のエージェント一覧を更新
