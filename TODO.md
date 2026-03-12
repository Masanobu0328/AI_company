# TODO

最終更新: 2026-03-12

## 完了済み ✅

- [x] Google Drive MCP 接続確認
- [x] リポジトリ設計刷新（INPUT/OUTPUT完全分離）
  - Obsidian Vault = CEOの脳（読み取り専用）
  - GitHub = 会社の全アウトプット
- [x] `knowledge/` フォルダ新設（ideas/research/clients/projects/playbooks）
- [x] `vault_schema/` 解体・テンプレートを `knowledge/_templates/` に統合
- [x] 各エージェントを `agent.md` に統合・`skills/` フォルダ新設
- [x] Discord Bot 作成・起動
- [x] Claude API（Haiku）接続
- [x] チャンネル別エージェント自動振り分け
- [x] CEO専用アクセス制限（ユーザーID制限）
- [x] `agent.md` をBotが起動時に自動読み込み
- [x] 応答スタイル最適化（基本3行・詳細は要求時のみ）

---

## 次回TODO

### 優先度：高
- [ ] PCスリープ設定変更（Bot常時稼働のため）
- [ ] Discordチャンネル構成の最終整備
- [ ] Botの起動を自動化（PC起動時に自動スタート）

### 優先度：中
- [ ] VPSへの移行（Railway/Render）で24時間稼働
- [ ] エージェント稼働テスト（営業・PM・開発の連携）
- [ ] `knowledge/` への実績データ蓄積開始

### 優先度：低
- [ ] Discord以外の入力チャンネル検討（LINE / Slack等）
- [ ] モデルをHaikuからSonnetに変更（本格稼働時）

---

## 接続状況
| サービス | 状態 |
|---|---|
| GitHub (AI_company) | ✅ |
| Google Drive MCP | ✅ 読み取り専用 |
| Gmail MCP | ✅ |
| Google Calendar MCP | ✅ |
| Discord Bot | ✅ 稼働中（ローカルPC） |
| サーバー（VPS） | ❌ 未設定 |
