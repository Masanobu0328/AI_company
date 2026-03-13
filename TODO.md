# TODO

最終更新: 2026-03-12

## 完了済み ✅

- [x] Google Drive MCP 接続確認
- [x] リポジトリ設計刷新（INPUT/OUTPUT完全分離）
- [x] `knowledge/` フォルダ新設
- [x] 各エージェントを `agent.md` に統合・`skills/` フォルダ新設
- [x] Discord Bot 作成・起動
- [x] Claude API（Haiku）接続
- [x] チャンネル別エージェント自動振り分け
- [x] CEO専用アクセス制限
- [x] `agent.md` をBotが起動時に自動読み込み
- [x] 応答スタイル最適化
- [x] Discordチャンネル構成の最終整備
  - チャンネル名：名前＋役割形式
  - Webhook導入：各エージェントが独自の名前・アイコンで発言
  - エージェント別学習ログ（チャンネル内で「覚えて」）
  - #agent-chat：全体会議 & エージェント間自動会話
  - #task-board：タスク進捗の自動通知

---

## 次回TODO

### 優先度：高
- [ ] PCスリープ設定変更（Bot常時稼働のため）
- [ ] Botの起動を自動化（PC起動時に自動スタート）
- [ ] エージェント自律化①：定期スタンドアップ（PMが毎朝自動で会議を開始）
- [ ] エージェント自律化②：#agent-chat の会話を自動でGitHubに保存・学習

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
| Discord Bot | ✅ 稼働中（ローカルPC・手動起動） |
| サーバー（VPS） | ❌ 未設定 |
