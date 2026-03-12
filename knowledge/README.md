# ナレッジベース

会社が生成・蓄積したナレッジを管理するフォルダ。
エージェントのアウトプット（リサーチ・クライアント情報・アイデア・実績パターン）はすべてここに保存する。

## フォルダ構成

```
knowledge/
├── _templates/     ノート作成用テンプレート
├── ideas/          アイデア・着想
├── research/       市場調査・競合・業界分析
├── clients/        クライアント情報・商談履歴
├── projects/       プロジェクト管理・進捗
└── playbooks/      実績から生まれたノウハウ・再現可能な型
```

## 保存ルール
1. すべてのノートはMarkdown形式で保存する
2. ファイル先頭にFrontmatterを必ず記述する（title / 作成日 / 更新日 / 作成者 / tags / status）
3. 更新時は `更新日` を書き換え、内容は追記する（上書き禁止）
4. テンプレートは `_templates/` を使用する

## Frontmatter標準形式
```yaml
---
title: [タイトル]
作成日: YYYY-MM-DD
更新日: YYYY-MM-DD
作成者: [エージェント名]
tags: [タグ1, タグ2]
status: draft / active / archived
---
```
