# AI会社 - システム指示書

## 基本方針
- すべての出力・ログ・ドキュメントは日本語で記述すること
- 各エージェントはモジュール型プラグインとして独立して動作すること
- Discord向けの出力はMarkdown形式で適切にフォーマットすること
- ナレッジベースはObsidian Vault（Google Drive同期）に保存すること

## ディレクトリ構造
```
agents/      → エージェント設定（各エージェントのclaude.mdとskills.md）
workflows/   → 業務フロー定義
logs/        → GitHubリポジトリに保存する活動ログ
knowledge_base/ → Obsidian連携ナレッジベース
dashboard/   → CEOダッシュボード
```

## エージェント呼び出しルール
- タスク依頼は必ずPM（プロジェクトマネージャー）を通すこと
- 緊急事項はSecretaryに直接連絡
- すべてのアウトプットはlogsに記録すること

## 拡張ルール
新しいエージェントを追加する場合：
1. `agents/<エージェント名>/` フォルダを作成
2. `claude.md`（役割・指示）と`skills.md`（能力定義）を作成
3. `README.md`のエージェント一覧を更新

## ナレッジベース操作ルール
- ノートは必ず `knowledge_base/` 配下に保存する
- フォルダ: `ideas/`（着想）`research/`（調査）`clients/`（顧客）`projects/`（案件）
- 全ノートにFrontmatter（title / 作成日 / 更新日 / 作成者 / tags / status）を記述する
- 既存ノートを更新する場合は `更新日` を書き換え、内容は上書きせず追記する
- テンプレートは `knowledge_base/_templates/` を使用する
- 詳細操作手順は `knowledge_base/agents_kb_guide.md` を参照すること
