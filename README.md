# AI会社 - 運営システム

## 概要
AIエージェントによって運営される会社の中枢システムリポジトリ。
CEOが指揮を執り、各AIエージェントが専門領域を担当する。

---

## ストレージ設計

```
【Obsidian Vault (Google Drive同期)】  ←  ナレッジベース
  ideas/       アイデア・着想
  research/    市場調査・競合・見込み客分析
  clients/     クライアント情報・商談履歴
  projects/    プロジェクト管理・進捗

【GitHub: AI_company】  ←  システム・ログ（このリポジトリ）
  agents/      エージェント定義
  workflows/   業務フロー
  logs/        活動ログ
  dashboard/   CEOダッシュボード
  vault_schema/ Vaultの構造定義・テンプレート
```

---

## このリポジトリの構造
- `agents/` — 各AIエージェントの設定と能力定義
- `workflows/` — 業務フロー定義
- `logs/` — 全エージェントの活動ログ
- `dashboard/` — CEOダッシュボード
- `vault_schema/` — Obsidian Vaultの構造定義・テンプレート（参照用）

## エージェント一覧
| エージェント | 役割 |
|---|---|
| secretary | CEO秘書・タスク管理 |
| pm | プロジェクトマネージャー |
| sales | 営業・クライアント獲得 |
| marketing | マーケティング・リード獲得 |
| development | 開発・Web制作 |

## 言語ポリシー
すべてのドキュメント、エージェント出力、ログは日本語で記述すること。
