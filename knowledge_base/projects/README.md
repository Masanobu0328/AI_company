---
title: プロジェクトフォルダ インデックス
作成日: 2026-03-11
更新日: 2026-03-11
作成者: システム
tags: [インデックス, プロジェクト]
---

# プロジェクト

## 概要
成約後のプロジェクト管理・進捗・納品物を記録するフォルダ。

## フォルダ構成
```
projects/
├── README.md                  # このファイル
└── [プロジェクト名]/
    ├── brief.md               # プロジェクトブリーフ・要件定義
    ├── progress.md            # 進捗ログ
    ├── deliverables.md        # 納品物リスト
    └── technical_notes.md     # 技術メモ（開発エージェント用）
```

## プロジェクトステータス
| ステータス | 説明 |
|---|---|
| planning | 計画・要件定義中 |
| active | 開発・制作進行中 |
| review | レビュー・修正中 |
| delivered | 納品完了・承認待ち |
| completed | 全工程完了 |
| on_hold | 保留中 |

## 担当エージェント
- **PMエージェント** — プロジェクト全体管理・progress.md 更新
- **開発エージェント** — deliverables.md / technical_notes.md 更新
- **営業エージェント** — brief.md 作成・クライアント窓口

## 関連フォルダ
- [[clients/README]] — クライアント情報
