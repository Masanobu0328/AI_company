# ナレッジベース

## 概要
Obsidian Vault（Google Drive同期）で管理するナレッジベース。

## 構造
```
knowledge_base/
├── clients/      # クライアント情報
├── templates/    # テンプレート集
├── research/     # リサーチデータ
└── processes/    # プロセスドキュメント
```

## 利用ルール
1. ファイルはMarkdown形式で保存
2. タグを使って検索可能にする
3. クライアント情報は必ず`clients/`に保存
4. テンプレートは定期的に更新する

## Obsidian連携
- Google Driveと自動同期
- エージェントはMarkdownファイルを読み書きする
- リンク（[[]]形式）を活用して情報を相互参照する
