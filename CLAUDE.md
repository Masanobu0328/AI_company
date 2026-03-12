# AI会社 - システム指示書

## 基本方針
- すべての出力・ログ・ドキュメントは日本語で記述すること
- 各エージェントはモジュール型プラグインとして独立して動作すること
- Discord向けの出力はMarkdown形式で適切にフォーマットすること

---

## ストレージ設計（重要）

### INPUTとOUTPUTを完全に分離する

| ストレージ | 役割 | エージェントの操作 |
|---|---|---|
| **Obsidian Vault**（Google Drive） | CEOの脳・思考・知識 | **読み取りのみ・絶対に書き込まない** |
| **GitHub**（AI_companyリポジトリ） | 会社の全アウトプット | 読み書き両方 |

---

## Obsidian Vault（CEOのINPUT）

**Google Drive フォルダID**: `1DbXDxY9Hif_1LlASrUmm7JLcMe2pPReC`
（Google Drive MCP経由でアクセス。サーバー名: gdrive）

### ⚠️ 絶対ルール
> **Vault内のいかなるファイル・フォルダも編集・削除・作成・上書き禁止。**
> CEOの個人ノート・思考・知的財産が含まれており、参照のみ許可。

### 用途
- CEOの考え・アイデア・判断軸を読み取り、意思決定の参考にする
- エージェントはVaultを「CEOの脳」として参照し、その思想に沿った行動をとる

---

## GitHub（会社のOUTPUT）

**URL**: https://github.com/Masanobu0328/AI_company

### フォルダ構成
```
AI_company/
├── agents/       エージェント定義（claude.md / skills.md）
├── workflows/    業務フロー定義
├── knowledge/    会社が生成したナレッジ（リサーチ・クライアント情報・アイデア）
├── logs/         全エージェントの活動ログ
└── dashboard/    CEOダッシュボード・レポート
```

### ルール
1. 会社が生成した全アウトプットはGitHubに保存する
2. `knowledge/` にはMarkdown形式で保存し、Frontmatterを必ず記述する（title / 作成日 / 更新日 / 作成者 / tags / status）
3. ログは `logs/YYYY-MM-DD_[種別]_[概要].md` で記録する
4. 重要な変更はコミットメッセージに日本語で記述する

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
