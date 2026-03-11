# Obsidian Vault 構造定義

## Vault パス
- **Google Drive フォルダID**: `1DbXDxY9Hif_1LlASrUmm7JLcMe2pPReC`
- **Google Drive URL**: https://drive.google.com/drive/folders/1DbXDxY9Hif_1LlASrUmm7JLcMe2pPReC
- **MCP アクセス方法**: `gdrive` MCPサーバー経由（読み書き対応）

## フォルダ構造
```
[Obsidian Vault]/
├── ideas/                    # アイデア・着想
│   └── YYYY-MM-DD_[タイトル].md
├── research/                 # リサーチ・調査
│   ├── market/               # 市場・業界調査
│   ├── competitors/          # 競合分析
│   └── prospects/            # 見込み客サイト分析
├── clients/                  # クライアント情報
│   └── [企業名]/
│       ├── [企業名]_overview.md   # 基本情報
│       ├── outreach.md            # 連絡・アウトリーチ履歴
│       ├── discovery.md           # ディスカバリーメモ
│       └── brief.md               # プロジェクトブリーフ（成約後）
└── projects/                 # プロジェクト管理
    └── [プロジェクト名]/
        ├── brief.md               # 要件定義
        ├── progress.md            # 進捗ログ
        ├── deliverables.md        # 納品物リスト
        └── technical_notes.md     # 技術メモ
```

## フォルダ別担当エージェント
| フォルダ | 主担当 | 操作 |
|---|---|---|
| ideas/ | 全エージェント | 作成・更新 |
| research/ | 営業・マーケティング | 作成・更新 |
| clients/ | 営業 | 作成・更新 |
| projects/ | PM・開発 | 作成・更新 |

## Frontmatter 標準形式
```yaml
---
title: [タイトル]
作成日: YYYY-MM-DD
更新日: YYYY-MM-DD
作成者: [エージェント名]
tags: [タグ1, タグ2]
status: [draft / active / archived]
links: []
---
```

## 標準タグ
| タグ | 用途 |
|---|---|
| #クライアント | クライアント関連 |
| #リサーチ | 調査・分析 |
| #アイデア | アイデア・着想 |
| #プロジェクト | プロジェクト管理 |
| #営業 | 営業活動 |
| #マーケティング | マーケティング |
| #開発 | 開発・技術 |
| #重要 | 優先度高 |
| #アーカイブ | 完了・保存のみ |

## ファイル命名規則
```
# 通常ノート
YYYY-MM-DD_[タイトル].md

# クライアントノート
clients/[企業名]/[企業名]_overview.md

# プロジェクトノート
projects/[プロジェクト名]/brief.md
```

## 接続方法
- **現在**: Google Drive MCP（`gdrive` サーバー、読み書き対応）✅
- **将来**: サーバー運用時も同じMCPをリモートで動作させる
