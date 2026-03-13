# TODO

最終更新: 2026-03-13

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
  - Webhook導入：各エージェントが独自の名前・アイコンで発言
  - エージェント別学習ログ（チャンネル内で「覚えて」）
  - #agent-chat：全体会議 & エージェント間自動会話
  - #task-board：タスク進捗の自動通知
- [x] 3層メモリ構造の実装
  - Layer1: agents/[名前]/memory.md（個人記憶）+ knowledge/shared/（全体）
  - Layer2: 直近10ターンの会話履歴
  - Layer3: logs/ に全会話保存・毎日23:59に自動push
- [x] 学習の二重保存（キーワードトリガー + エージェント自動判断[SAVE:]）
- [x] エージェント間メッセージング（[MSG:agent:]・[SHARE:]）
- [x] GitHub API直接書き込み（gitコマンド不要）
- [x] 朝会の自動実行（毎朝9時）+ Threads投稿案3本
- [x] モデル自動切り替え（会話→Haiku / スキル実行→Sonnet）
- [x] Web検索ツール統合（Sonnet使用時に自動有効）
- [x] [FILE:] 成果物自動GitHub保存システム
- [x] ゴールドコーストプロジェクト開始
  - 各エージェントの役割定義
  - プロジェクトフォルダ構造作成（projects/goldcoast/）

---

## 次回TODO

### 優先度：高（次回セッションでやること）

- [ ] **PCスリープ設定変更**（Botが落ちないようにスリープ無効化）
- [ ] **Bot起動の自動化**（PC起動時にタスクスケジューラで自動スタート）
- [ ] **会社用Googleアカウント作成**（Bot専用・個人アカウントと分離）
  - 作成後：Google Cloud Project設定
  - Sheets API / Gmail API / Drive API を有効化
  - Service Account認証ファイルを発行 → .envに追加
  - BotからSheets書き込み・Gmail送信ができるようにする
- [ ] **ゴールドコーストプロジェクトを実際に回す**
  - グラントに営業リスト作成を依頼（Discord #グラント-営業）
  - 森岡にポジショニング分析を依頼（Discord #森岡-マーケティング）
  - ウォズニアックにLP第一弾モックアップ依頼

### 優先度：中

- [ ] VPSへの移行（Railway/Render）で24時間稼働
- [ ] Vercel自動デプロイ設定（GitHub push → 自動反映）
- [ ] Gemini APIの検討（画像生成・モックアップ用途）

### 優先度：低

- [ ] OpenClaw（Claude Computer Use）導入で完全自律化
- [ ] RAG実装（ログが溜まってから）
- [ ] Discord以外の入力チャンネル検討（LINE / Slack等）
- [ ] NotebookLM活用検討

---

## 接続状況
| サービス | 状態 |
|---|---|
| GitHub (AI_company) | ✅ API直接書き込み対応 |
| Google Drive MCP | ✅ 読み取り専用（Claude Code経由） |
| Gmail MCP | ✅ Claude Code経由のみ・Bot未接続 |
| Google Calendar MCP | ✅ Claude Code経由のみ・Bot未接続 |
| Discord Bot | ✅ 稼働中（ローカルPC・手動起動） |
| Web検索 | ✅ Anthropic web_search統合済み |
| Google Sheets | ❌ 未設定（会社用Gアカウント作成後に対応） |
| サーバー（VPS） | ❌ 未設定 |
