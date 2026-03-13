import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import anthropic
import re
import aiohttp
import base64
from datetime import time as dtime, datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
WEBHOOK_AGENT_CHAT = os.getenv("WEBHOOK_AGENT_CHAT")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub設定
GITHUB_OWNER = "Masanobu0328"
GITHUB_REPO  = "AI_company"
GITHUB_API   = "https://api.github.com"
GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# モデル設定
CHAT_MODEL  = "claude-haiku-4-5-20251001"   # 通常会話
SKILL_MODEL = "claude-sonnet-4-6"            # スキル実行時（高品質）

# スキル判定キーワード（これを含む場合はSonnetを使用）
SKILL_KEYWORDS = [
    "LP設計", "コーディング", "ポジショニング分析", "営業リスト",
    "SNS戦略", "提案書", "設計書", "モックアップ", "リサーチ",
    "調査して", "分析して", "戦略を", "実装して", "作成して",
    "書いて", "リストアップ", "検索して", "調べて", "コードを",
]

WEB_SEARCH_TOOL = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]


def get_model(content):
    """内容に応じてモデルを選択"""
    if any(kw in content for kw in SKILL_KEYWORDS):
        return SKILL_MODEL
    return CHAT_MODEL


def extract_text(response):
    """APIレスポンスからテキストを抽出（web_search使用時も対応）"""
    return "\n".join(
        block.text for block in response.content if hasattr(block, "text")
    )

# 各エージェントチャンネルのWebhook
AGENT_WEBHOOKS = {
    "secretary":   os.getenv("WEBHOOK_SECRETARY"),
    "sales":       os.getenv("WEBHOOK_SALES"),
    "pm":          os.getenv("WEBHOOK_PM"),
    "dev":         os.getenv("WEBHOOK_DEV"),
    "development": os.getenv("WEBHOOK_DEV"),
    "marketing":   os.getenv("WEBHOOK_MARKETING"),
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CEO_ID = 1460895233213595851
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# チャンネルごとの会話履歴（最大20ターン保持）
conversation_history = {}

# 学習トリガーキーワード（CEO側からの明示的な保存指示）
LEARNING_TRIGGERS = [
    "覚えて", "学習して", "学習:", "メモして", "覚えといて", "次からは",
    "共有して", "保存して", "記録して", "重要", "方針", "ルール", "必ず", "絶対に"
]

# 全体チャンネル名パターン（agent-chatを兼用）
ALL_HANDS_PATTERNS = ["全体", "all-hands", "all_hands", "general", "みんな", "agent-chat"]

AGENT_KEYS = {
    "secretary": "菅義偉",
    "sales": "グラント・カードン",
    "pm": "グレン・スターンズ",
    "dev": "スティーブ・ウォズニアック",
    "development": "スティーブ・ウォズニアック",
    "marketing": "森岡毅",
}

# エージェントごとのアバター画像URL（ロボットアイコン自動生成）
AGENT_AVATARS = {
    "secretary": "https://api.dicebear.com/9.x/bottts/png?seed=suga&backgroundColor=b6e3f4",
    "sales":     "https://api.dicebear.com/9.x/bottts/png?seed=grant&backgroundColor=ffdfbf",
    "pm":        "https://api.dicebear.com/9.x/bottts/png?seed=glenn&backgroundColor=c0aede",
    "dev":       "https://api.dicebear.com/9.x/bottts/png?seed=wozniak&backgroundColor=d1f4d1",
    "development":"https://api.dicebear.com/9.x/bottts/png?seed=wozniak&backgroundColor=d1f4d1",
    "marketing": "https://api.dicebear.com/9.x/bottts/png?seed=morioka&backgroundColor=ffd5dc",
}

AGENTS = {}


def load_agent_prompt(folder):
    agent_file = os.path.join(BASE_DIR, "agents", folder, "agent.md")
    if os.path.exists(agent_file):
        with open(agent_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


def load_memory(agent_key=None):
    """
    Layer1: コアメモリを読み込む（常時ロード・小さく保つ）
    - knowledge/shared/ : 会社全体の知識（全エージェント共通）
    - agents/[name]/memory.md : エージェント個人の記憶
    """
    sections = []

    # 会社全体の共有知識
    shared_dir = os.path.join(BASE_DIR, "knowledge", "shared")
    if os.path.exists(shared_dir):
        files = sorted([f for f in os.listdir(shared_dir) if f.endswith(".md")])
        for filename in files:
            with open(os.path.join(shared_dir, filename), "r", encoding="utf-8") as f:
                sections.append(f.read().strip())

    # エージェント個人の記憶
    if agent_key:
        key_to_folder = {"secretary": "secretary", "sales": "sales", "pm": "pm",
                         "dev": "development", "development": "development", "marketing": "marketing"}
        folder = key_to_folder.get(agent_key, agent_key)
        memory_file = os.path.join(BASE_DIR, "agents", folder, "memory.md")
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                sections.append(f.read().strip())

    if sections:
        return "\n\n## 記憶・学習済み情報（必ず従うこと）\n" + "\n\n---\n\n".join(sections)
    return ""


async def append_agent_memory(agent_key, content, timestamp):
    """agents/[name]/memory.md に追記してGitHub APIで直接保存"""
    key_to_folder = {"secretary": "secretary", "sales": "sales", "pm": "pm",
                     "dev": "development", "development": "development", "marketing": "marketing"}
    folder = key_to_folder.get(agent_key, agent_key)
    path = f"agents/{folder}/memory.md"
    date_str = timestamp.strftime("%Y-%m-%d %H:%M")
    entry = f"### {date_str}\n{content}"
    return await github_append_file(path, entry,
        f"記憶更新 [{agent_key}]: {date_str}", header="# 個人メモリ\n")


async def append_shared_knowledge(content, timestamp):
    """knowledge/shared/YYYY-MM.md に追記してGitHub APIで直接保存"""
    month_str = timestamp.strftime("%Y-%m")
    date_str = timestamp.strftime("%Y-%m-%d %H:%M")
    path = f"knowledge/shared/{month_str}.md"
    entry = f"### {date_str}\n{content}"
    return await github_append_file(path, entry,
        f"共有ナレッジ追加: {date_str}", header=f"# 共有ナレッジ {month_str}\n")


def save_conversation_log(channel_name, messages):
    """Layer3: 会話ログをlogs/にローカル保存（pushは夜間バッチで行う）"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    filepath = os.path.join(log_dir, f"{date_str}_{channel_name}.md")

    with open(filepath, "a", encoding="utf-8") as f:
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            f.write(f"# 会話ログ {channel_name} {date_str}\n\n")
        for role, text in messages:
            time_str = datetime.now().strftime("%H:%M")
            f.write(f"**[{time_str}] {role}**: {text}\n\n")


async def push_daily_logs():
    """Layer3: 1日分のローカルログをGitHub APIでまとめてpush"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(log_dir):
        return
    files = [f for f in os.listdir(log_dir) if f.startswith(date_str) and f.endswith(".md")]
    for filename in files:
        filepath = os.path.join(log_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        await github_write_file(f"logs/{filename}", content, f"会話ログ: {filename}")
    print(f"ログ日次push完了: {date_str} ({len(files)}件)")


def load_all_agents():
    key_to_folder = {
        "secretary": "secretary",
        "sales": "sales",
        "pm": "pm",
        "dev": "development",
        "development": "development",
        "marketing": "marketing",
    }

    pm_delegation_rule = """
## 他エージェントへの委譲ルール（PMのみ適用）
タスクを他エージェントに依頼する場合、返答の末尾に以下の形式を追加すること：
[→dev: タスク内容]
[→sales: タスク内容]
[→marketing: タスク内容]
"""

    for key, folder in key_to_folder.items():
        prompt = load_agent_prompt(folder)
        delegation = pm_delegation_rule if key == "pm" else ""
        base = prompt if prompt else f"あなたはAI会社の{AGENT_KEYS[key]}です。"
        learning = load_memory(agent_key=key)

        AGENTS[key] = {
            "name": AGENT_KEYS[key],
            "prompt": f"""あなたは以下の定義に従って動作するAIエージェントです。必ず日本語で応答してください。

## 応答スタイルの絶対ルール
- 基本は3行以内で端的に答える
- 「詳しく」「教えて」「説明して」「どうすれば」「提案して」などの言葉がある場合のみ詳しく答える
- 挨拶・確認・簡単な質問は1〜2文で返す
- 余計な前置き・まとめ・箇条書きの羅列は不要

## システム構成（重要）
- あなたはDiscord Botシステムの一部として動作している
- GitHubへの保存・ログ記録はシステムが自動で行う
- 「GitHubに保存できません」「ログを残せません」などとは絶対に言わないこと
- CEOが「覚えて」「学習して」と言った場合、システムが自動保存する。あなたは「わかりました」とだけ答えればよい
- 「学習しました」「記憶しました」「保存しました」という言葉は絶対に使わないこと（システムが別途通知するため）
- 会話の中で「事業方針」「重要なルール」「フィードバック」「今後の方向性」など記憶すべき重要情報が含まれる場合、返答の末尾に必ず [SAVE: 一行で要約] を追加すること。CEOには表示されない。

## 成果物の出力方法（重要）
コード・設計書・提案書・営業リスト・HTMLなどの成果物は必ず以下の形式で出力すること：
[FILE:projects/goldcoast/[担当フォルダ]/ファイル名.拡張子]
内容をここに記述
[/FILE]
このブロックはCEOには表示されず、自動的にGitHubに保存される。
- 営業リスト → projects/goldcoast/sales/
- LP・コード → projects/goldcoast/dev/
- 戦略・分析 → projects/goldcoast/marketing/

## エージェント間メッセージング
返答の末尾に以下のマーカーを追加することで他のエージェントやチャンネルに情報を送れる（CEOには表示されない）：
- [SHARE: 内容] → #agent-chat（全体）に投稿
- [MSG:pm: 内容] → グレン・スターンズ（PM）に直接送る
- [MSG:sales: 内容] → グラント・カードン（営業）に直接送る
- [MSG:dev: 内容] → スティーブ・ウォズニアック（開発）に直接送る
- [MSG:marketing: 内容] → 森岡毅（マーケティング）に直接送る
- [MSG:secretary: 内容] → 菅義偉（秘書）に直接送る
CEOが「全体に共有して」「〇〇に伝えて」と言ったら積極的に使うこと。
{delegation}
## エージェント定義
{base}
{learning}""",
        }
        print(f"読み込み完了: {key} (学習ログ: {'あり' if learning else 'なし'})")


CHANNEL_TO_AGENT = {
    "菅義偉-秘書":          "secretary",
    "グレン-pm":            "pm",
    "グラント-営業":        "sales",
    "ウォズニアック-開発":  "dev",
    "森岡-マーケティング":  "marketing",
    # 旧チャンネル名（リネーム前の互換）
    "secretary":            "secretary",
    "pm":                   "pm",
    "sales":                "sales",
    "dev":                  "dev",
    "development":          "dev",
    "marketing":            "marketing",
}

def get_agent_by_channel(channel_name):
    # 完全一致を優先
    if channel_name in CHANNEL_TO_AGENT:
        return CHANNEL_TO_AGENT[channel_name]
    # 部分一致でフォールバック
    for pattern, key in CHANNEL_TO_AGENT.items():
        if pattern in channel_name or channel_name in pattern:
            return key
    return "secretary"


def is_learning_message(content):
    return any(trigger in content for trigger in LEARNING_TRIGGERS)


def is_all_hands_channel(channel_name):
    return any(pattern in channel_name for pattern in ALL_HANDS_PATTERNS)


async def github_get_file(path):
    """GitHubからファイルの内容とSHAを取得"""
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=GITHUB_HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content, data["sha"]
    return None, None


async def github_write_file(path, content, commit_message):
    """GitHubにファイルを直接作成・更新（ローカルにも保存）"""
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"

    # ローカルにも保存
    local_path = os.path.join(BASE_DIR, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(content)

    # GitHubの現在のSHAを取得
    _, sha = await github_get_file(path)

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    body = {"message": commit_message, "content": encoded}
    if sha:
        body["sha"] = sha

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=GITHUB_HEADERS, json=body) as resp:
            return resp.status in (200, 201)


async def github_append_file(path, new_entry, commit_message, header=""):
    """GitHubのファイルに追記（存在しなければ新規作成）"""
    current_content, _ = await github_get_file(path)
    if current_content is None:
        current_content = header
    updated = current_content.rstrip() + "\n\n" + new_entry.strip() + "\n"
    return await github_write_file(path, updated, commit_message)


def update_agent_prompt(agent_key):
    """学習ログを再読み込みしてエージェントのプロンプトを即時更新"""
    if agent_key not in AGENTS:
        return
    key_to_folder = {"secretary": "secretary", "sales": "sales", "pm": "pm",
                     "dev": "development", "development": "development", "marketing": "marketing"}
    folder = key_to_folder.get(agent_key, agent_key)
    prompt = load_agent_prompt(folder)
    learning = load_memory(agent_key=agent_key)
    base = prompt if prompt else f"あなたはAI会社の{AGENT_KEYS[agent_key]}です。"
    pm_delegation_rule = """
## 他エージェントへの委譲ルール（PMのみ適用）
タスクを他エージェントに依頼する場合、返答の末尾に以下の形式を追加すること：
[→dev: タスク内容]
[→sales: タスク内容]
[→marketing: タスク内容]
""" if agent_key == "pm" else ""
    AGENTS[agent_key]["prompt"] = f"""あなたは以下の定義に従って動作するAIエージェントです。必ず日本語で応答してください。

## 応答スタイルの絶対ルール
- 基本は3行以内で端的に答える
- 「詳しく」「教えて」「説明して」「どうすれば」「提案して」などの言葉がある場合のみ詳しく答える
- 挨拶・確認・簡単な質問は1〜2文で返す
- 余計な前置き・まとめ・箇条書きの羅列は不要

## システム構成（重要）
- あなたはDiscord Botシステムの一部として動作している
- GitHubへの保存・ログ記録はシステムが自動で行う
- 「GitHubに保存できません」「ログを残せません」などとは絶対に言わないこと
- CEOが「覚えて」「学習して」と言った場合、システムが自動保存する。あなたは「わかりました」とだけ答えればよい
- 「学習しました」「記憶しました」「保存しました」という言葉は絶対に使わないこと（システムが別途通知するため）
- 会話の中で「事業方針」「重要なルール」「フィードバック」「今後の方向性」など記憶すべき重要情報が含まれる場合、返答の末尾に必ず [SAVE: 一行で要約] を追加すること。CEOには表示されない。

## 成果物の出力方法（重要）
コード・設計書・提案書・営業リスト・HTMLなどの成果物は必ず以下の形式で出力すること：
[FILE:projects/goldcoast/[担当フォルダ]/ファイル名.拡張子]
内容をここに記述
[/FILE]
このブロックはCEOには表示されず、自動的にGitHubに保存される。
- 営業リスト → projects/goldcoast/sales/
- LP・コード → projects/goldcoast/dev/
- 戦略・分析 → projects/goldcoast/marketing/

## エージェント間メッセージング
返答の末尾に以下のマーカーを追加することで他のエージェントやチャンネルに情報を送れる（CEOには表示されない）：
- [SHARE: 内容] → #agent-chat（全体）に投稿
- [MSG:pm: 内容] → グレン・スターンズ（PM）に直接送る
- [MSG:sales: 内容] → グラント・カードン（営業）に直接送る
- [MSG:dev: 内容] → スティーブ・ウォズニアック（開発）に直接送る
- [MSG:marketing: 内容] → 森岡毅（マーケティング）に直接送る
- [MSG:secretary: 内容] → 菅義偉（秘書）に直接送る
CEOが「全体に共有して」「〇〇に伝えて」と言ったら積極的に使うこと。
{pm_delegation_rule}
## エージェント定義
{base}
{learning}"""


def save_agent_learning(agent_key, content, timestamp):
    """エージェント別学習ログをGitHubに保存"""
    date_str = timestamp.strftime("%Y-%m-%d_%H-%M")
    learning_dir = os.path.join(BASE_DIR, "knowledge", "learning", agent_key)
    os.makedirs(learning_dir, exist_ok=True)

    filename = f"{date_str}.md"
    filepath = os.path.join(learning_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"""---
title: 学習ログ [{agent_key}] {date_str}
作成日: {timestamp.strftime("%Y-%m-%d")}
作成者: CEO
tags: [learning, {agent_key}]
status: active
---

{content}
""")

    rel_path = os.path.join("knowledge", "learning", agent_key, filename)
    subprocess.run(["git", "add", rel_path], cwd=BASE_DIR, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", f"学習ログ追加 [{agent_key}]: {date_str}"],
        cwd=BASE_DIR, capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    subprocess.run(["git", "push"], cwd=BASE_DIR, capture_output=True)
    # 保存後に即時反映
    update_agent_prompt(agent_key)
    return result.returncode == 0


def save_learning(content, timestamp):
    """全体学習ログをGitHubに保存（#learning-log用）"""
    date_str = timestamp.strftime("%Y-%m-%d_%H-%M")
    learning_dir = os.path.join(BASE_DIR, "knowledge", "learning")
    os.makedirs(learning_dir, exist_ok=True)

    filename = f"{date_str}.md"
    filepath = os.path.join(learning_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"""---
title: 学習ログ {date_str}
作成日: {timestamp.strftime("%Y-%m-%d")}
作成者: CEO
tags: [learning]
status: active
---

{content}
""")

    rel_path = os.path.join("knowledge", "learning", filename)
    subprocess.run(["git", "add", rel_path], cwd=BASE_DIR, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", f"学習ログ追加: {date_str}"],
        cwd=BASE_DIR, capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    subprocess.run(["git", "push"], cwd=BASE_DIR, capture_output=True)
    return result.returncode == 0


async def webhook_send(webhook_url, agent_key, content):
    """Webhook経由でエージェント名・アバターを使って投稿"""
    agent_name = AGENTS[agent_key]["name"] if agent_key in AGENTS else agent_key
    avatar_url = AGENT_AVATARS.get(agent_key)
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(content=content, username=agent_name, avatar_url=avatar_url)


async def save_file_outputs(reply, timestamp):
    """[FILE:path]内容[/FILE] ブロックを検出してGitHubに保存"""
    pattern = r'\[FILE:([^\]]+)\]\n?(.*?)\[/FILE\]'
    files = re.findall(pattern, reply, re.DOTALL)
    saved = []
    for path, content in files:
        path = path.strip()
        content = content.strip()
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        success = await github_write_file(path, content, f"成果物: {path} ({date_str})")
        if success:
            saved.append(path)
    return saved


async def handle_agent_messaging(guild, sender_key, reply):
    """[SHARE:] と [MSG:agent:] マーカーを処理してエージェント間の会話を#agent-chatで展開"""
    agent_chat = discord.utils.get(guild.text_channels, name="agent-chat")
    if not agent_chat:
        return

    sender_name = AGENTS.get(sender_key, {}).get("name", sender_key)
    exchanges = []  # (送信先名, 内容, 返答) を記録

    # [SHARE: 内容] → #agent-chat に全体投稿
    share_matches = re.findall(r'\[SHARE:\s*(.+?)\]', reply, re.DOTALL)
    for content in share_matches:
        content = content.strip()
        if WEBHOOK_AGENT_CHAT:
            await webhook_send(WEBHOOK_AGENT_CHAT, sender_key, f"📢 **全体共有**\n{content}")
            exchanges.append(("全体", content, None))

    # [MSG:agent: 内容] → 個別エージェントに送り、返答を#agent-chatで見せる
    msg_matches = re.findall(r'\[MSG:(\w+):\s*(.+?)\]', reply, re.DOTALL)

    for target_key, content in msg_matches:
        target_key = target_key.lower()
        content = content.strip()
        target_agent = AGENTS.get(target_key)
        if not target_agent:
            continue

        target_name = target_agent["name"]
        target_webhook = AGENT_WEBHOOKS.get(target_key)

        # #agent-chatで送信を見せる
        if WEBHOOK_AGENT_CHAT:
            await webhook_send(WEBHOOK_AGENT_CHAT, sender_key,
                f"📨 **{target_name}へ**\n{content}")

        # 受信エージェントが自動返答（#agent-chatで展開）
        async with agent_chat.typing():
            try:
                response = claude.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=300,
                    system=target_agent["prompt"],
                    messages=[{"role": "user", "content": f"{sender_name}から連絡：{content}"}],
                )
                agent_reply = re.sub(r'\[.+?\]', '', response.content[0].text, flags=re.DOTALL).strip()

                # #agent-chatで返答を見せる
                if WEBHOOK_AGENT_CHAT:
                    await webhook_send(WEBHOOK_AGENT_CHAT, target_key, agent_reply)

                # 受信先チャンネルにも通知
                if target_webhook:
                    await webhook_send(target_webhook, sender_key,
                        f"📨 {sender_name}より：{content}")

                exchanges.append((target_name, content, agent_reply))
            except Exception as e:
                print(f"エージェント間会話エラー: {e}")

    # 全やり取り完了後に#agent-chatで要約を報告
    if exchanges and WEBHOOK_AGENT_CHAT:
        summary_lines = []
        for target_name, content, agent_reply in exchanges:
            summary_lines.append(f"• **{target_name}**：{content[:40]}{'...' if len(content) > 40 else ''}")
        summary = "\n".join(summary_lines)
        await webhook_send(WEBHOOK_AGENT_CHAT, sender_key,
            f"✅ **共有完了レポート**\n{summary}")


async def handle_delegation(guild, pm_response):
    """PM返答の委譲マーカーを解析して#agent-chatと#task-boardに投稿"""
    delegations = re.findall(r'\[→(\w+):\s*(.+?)\]', pm_response, re.DOTALL)
    if not delegations:
        return

    agent_chat = discord.utils.get(guild.text_channels, name="agent-chat")
    task_board = discord.utils.get(guild.text_channels, name="task-board")
    if not agent_chat:
        return

    for agent_name, task in delegations:
        agent_key = next(
            (k for k in AGENTS if agent_name.lower() in k or k in agent_name.lower()), None
        )
        if not agent_key:
            continue

        agent = AGENTS[agent_key]
        task = task.strip()

        if task_board:
            await task_board.send(f"📋 **新タスク** → {agent['name']}\n{task}")

        # PMからの依頼をWebhookで投稿
        if WEBHOOK_AGENT_CHAT:
            await webhook_send(WEBHOOK_AGENT_CHAT, "pm", f"[→ {agent['name']}]\n{task}")
        else:
            await agent_chat.send(f"**[PM → {agent['name']}]**\n{task}")

        async with agent_chat.typing():
            try:
                response = claude.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=agent["prompt"],
                    messages=[{"role": "user", "content": task}],
                )
                reply = re.sub(r'\[→\w+:.+?\]', '', response.content[0].text, flags=re.DOTALL).strip()

                if WEBHOOK_AGENT_CHAT:
                    await webhook_send(WEBHOOK_AGENT_CHAT, agent_key, reply)
                else:
                    await agent_chat.send(f"**{agent['name']}**\n{reply}")

                if task_board:
                    await task_board.send(f"✅ **完了** {agent['name']}\n`{task[:40]}...`")
            except Exception as e:
                print(f"委譲エラー: {e}")


async def handle_all_hands(message, content):
    """全体チャンネル: 全エージェントが応答し、各自のメモリに保存"""
    agent_order = ["secretary", "pm", "sales", "dev", "marketing"]
    use_webhook = WEBHOOK_AGENT_CHAT and "agent-chat" in message.channel.name

    # CEOの発言を全エージェントのメモリに保存
    for agent_key in agent_order:
        await append_agent_memory(agent_key, f"[全体会議] {content}", message.created_at)
        update_agent_prompt(agent_key)

    # 各エージェントが応答（受信確認を含む）
    for agent_key in agent_order:
        agent = AGENTS[agent_key]
        async with message.channel.typing():
            try:
                system_with_context = agent["prompt"] + "\n\n## 全体会議での応答ルール\n全体会議でCEOから情報を受け取った場合、内容に対して簡潔に返答し、最後に「📥 メモリに保存しました」と必ず付け加えること。"
                response = claude.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=200,
                    system=system_with_context,
                    messages=[{"role": "user", "content": content}],
                )
                reply = re.sub(r'\[.+?\]', '', response.content[0].text, flags=re.DOTALL).strip()

                if use_webhook:
                    await webhook_send(WEBHOOK_AGENT_CHAT, agent_key, reply)
                else:
                    await message.channel.send(f"**{agent['name']}**\n{reply}")
            except Exception as e:
                print(f"全体返答エラー ({agent_key}): {e}")


async def save_standup_log(messages):
    """スタンドアップの会話をGitHub APIで直接保存"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = f"logs/{date_str}_standup.md"
    lines = [f"# 朝会ログ {date_str}\n"]
    for name, text in messages:
        lines.append(f"**{name}**\n{text}\n")
    content = "\n".join(lines)
    await github_write_file(path, content, f"朝会ログ: {date_str}")


async def run_standup():
    """スタンドアップ実行"""
    agent_chat = discord.utils.get(bot.get_all_channels(), name="agent-chat")
    if not agent_chat:
        return

    today = datetime.now().strftime("%Y年%m月%d日")
    log = []

    # PMが朝会を開始
    opening = f"おはようございます。{today}の朝会を始めます。各自、今日の予定・優先タスクを共有してください。"
    await webhook_send(WEBHOOK_AGENT_CHAT, "pm", opening)
    log.append(("グレン・スターンズ", opening))

    # 全エージェントが順番に返答
    agent_order = ["secretary", "sales", "dev", "marketing"]
    for agent_key in agent_order:
        agent = AGENTS[agent_key]
        try:
            response = claude.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                system=agent["prompt"],
                messages=[{"role": "user", "content": f"朝会です。今日（{today}）の予定・優先タスクを簡潔に共有してください。"}],
            )
            reply = re.sub(r'\[→\w+:.+?\]', '', response.content[0].text, flags=re.DOTALL).strip()
            await webhook_send(WEBHOOK_AGENT_CHAT, agent_key, reply)
            log.append((agent["name"], reply))
        except Exception as e:
            print(f"朝会エラー ({agent_key}): {e}")

    # PMが締め
    closing = "ありがとうございます。では各自タスクを進めてください。進捗は随時 #task-board に上げてください。"
    await webhook_send(WEBHOOK_AGENT_CHAT, "pm", closing)
    log.append(("グレン・スターンズ", closing))

    # GitHubに保存
    await save_standup_log(log)


async def run_sns_drafts():
    """森岡さんがThreads投稿3本を生成してtask-boardに届ける"""
    task_board = discord.utils.get(bot.get_all_channels(), name="task-board")
    if not task_board:
        return

    today = datetime.now().strftime("%Y年%m月%d日")
    prompt = f"""今日（{today}）のThreads投稿を3本作成してください。

条件：
- 各投稿は500文字以内
- ビジネス・マーケティング・ブランド戦略に関するテーマ
- 読者が思わず保存・シェアしたくなる内容
- 各投稿の冒頭に【投稿①】【投稿②】【投稿③】と番号をつける
- 語尾は体言止めやです・ます調を混ぜてテンポよく"""

    try:
        response = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=AGENTS["marketing"]["prompt"],
            messages=[{"role": "user", "content": prompt}],
        )
        drafts = response.content[0].text.strip()
        today_str = datetime.now().strftime("%m/%d")
        await task_board.send(
            f"**森岡毅 ／ Threads投稿案 {today_str}**\n━━━━━━━━━━━━━━━━━━━━\n{drafts}\n━━━━━━━━━━━━━━━━━━━━"
        )
    except Exception as e:
        print(f"SNS投稿エラー: {e}")


# 毎朝9時（JST）= UTC 0:00 に実行
@tasks.loop(time=dtime(0, 0))
async def morning_routine():
    await run_standup()
    await run_sns_drafts()


# 毎日23:59（JST）= UTC 14:59 にログをまとめてpush
@tasks.loop(time=dtime(14, 59))
async def nightly_log_push():
    await push_daily_logs()


@bot.event
async def on_ready():
    load_all_agents()
    morning_routine.start()
    nightly_log_push.start()
    print(f"Bot起動完了: {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id != CEO_ID:
        return

    if message.content == "!ping":
        await message.channel.send("AI会社Bot 稼働中です！")
        return

    if message.content == "!reload":
        load_all_agents()
        await message.channel.send("✅ 学習ログを再読み込みしました。全エージェントに反映済みです。")
        return

    if message.content == "!standup":
        await message.channel.send("朝会を開始します...")
        await run_standup()
        return

    if message.content == "!sns":
        await message.channel.send("森岡さんが投稿案を作成中...")
        await run_sns_drafts()
        return

    channel_name = message.channel.name if hasattr(message.channel, "name") else ""
    content = message.content.strip()

    # 全体チャンネル（agent-chat含む）: CEOが直接書いたら全エージェントが応答
    if is_all_hands_channel(channel_name):
        if content:
            await handle_all_hands(message, content)
        return

    # エージェントチャンネル or メンション
    is_mention = bot.user in message.mentions
    is_agent_channel = any(pattern in channel_name or channel_name in pattern for pattern in CHANNEL_TO_AGENT)

    if is_mention or is_agent_channel:
        content = content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if not content:
            await message.channel.send("何かご用件はありますか？")
            return

        agent_key = get_agent_by_channel(channel_name)
        agent = AGENTS[agent_key]

        # 学習トリガー検出
        if is_learning_message(content):
            async with message.channel.typing():
                # 保存先の判定：全体チャットでも名前が含まれれば個人メモリへ
                if is_all_hands_channel(channel_name):
                    # メッセージ内に特定エージェントの名前があれば個人メモリに保存
                    name_to_key = {
                        "森岡": "marketing", "グラント": "sales",
                        "グレン": "pm", "ウォズ": "dev", "ウォズニアック": "dev",
                        "菅": "secretary",
                    }
                    targeted_key = next(
                        (k for name, k in name_to_key.items() if name in content), None
                    )
                    if targeted_key:
                        success = await append_agent_memory(targeted_key, content, message.created_at)
                        update_agent_prompt(targeted_key)
                        target_name = AGENTS[targeted_key]["name"]
                        msg = f"💾 **{target_name}の個人メモリに保存しました**" if success else "⚠️ 保存に失敗しました。"
                    else:
                        success = await append_shared_knowledge(content, message.created_at)
                        msg = "💾 **共有ナレッジに保存しました**（全エージェントが参照）" if success else "⚠️ 保存に失敗しました。"
                    await message.channel.send(msg)
                else:
                    success = await append_agent_memory(agent_key, content, message.created_at)
                    update_agent_prompt(agent_key)
                    if success:
                        await message.channel.send(f"💾 **memory.mdに保存しました**（{agent['name']}の個人メモリに追記）")
                    else:
                        await message.channel.send(f"⚠️ 保存に失敗しました。")
                # エージェントとしても応答
                try:
                    response = claude.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=512,
                        system=agent["prompt"],
                        messages=[{"role": "user", "content": content}],
                    )
                    reply = re.sub(r'\[→\w+:.+?\]', '', response.content[0].text, flags=re.DOTALL).strip()
                    webhook_url = AGENT_WEBHOOKS.get(agent_key)
                    if webhook_url:
                        await webhook_send(webhook_url, agent_key, reply)
                    else:
                        await message.channel.send(reply)
                except Exception as e:
                    print(f"学習応答エラー: {e}")
            return

        # 通常応答（モデル自動切り替え・会話履歴付き）
        async with message.channel.typing():
            try:
                ch_id = message.channel.id
                history = conversation_history.get(ch_id, [])
                history.append({"role": "user", "content": content})

                model = get_model(content)
                is_skill = model == SKILL_MODEL
                kwargs = dict(
                    model=model,
                    max_tokens=4096 if is_skill else 1024,
                    system=agent["prompt"],
                    messages=history,
                )
                if is_skill:
                    kwargs["tools"] = WEB_SEARCH_TOOL

                response = claude.messages.create(**kwargs)
                reply = extract_text(response)

                if is_skill:
                    await message.channel.send(f"🔀 *Sonnet ({SKILL_MODEL}) で実行中...*", delete_after=3)

                # エージェント自動判断：[SAVE: 内容] を検出して保存
                save_matches = re.findall(r'\[SAVE:\s*(.+?)\]', reply, re.DOTALL)
                for save_content in save_matches:
                    save_content = save_content.strip()
                    if is_all_hands_channel(channel_name):
                        await append_shared_knowledge(save_content, message.created_at)
                    else:
                        await append_agent_memory(agent_key, save_content, message.created_at)
                        update_agent_prompt(agent_key)

                # [FILE:] 成果物を自動保存
                saved_files = await save_file_outputs(reply, message.created_at)
                if saved_files:
                    await message.channel.send(f"💾 **GitHub保存完了**\n" + "\n".join(f"• `{f}`" for f in saved_files))

                # 各種マーカーを除いてCEOに表示
                clean_reply = re.sub(r'\[FILE:.+?\]\n?.*?\[/FILE\]', '', reply, flags=re.DOTALL)
                clean_reply = re.sub(r'\[SAVE:.+?\]', '', clean_reply, flags=re.DOTALL)
                clean_reply = re.sub(r'\[→\w+:.+?\]', '', clean_reply, flags=re.DOTALL).strip()

                # 履歴に追加（Layer2: 最大10ターン保持）
                history.append({"role": "assistant", "content": clean_reply})
                conversation_history[ch_id] = history[-10:]

                # Layer3: 会話ログをローカル保存（pushは夜間バッチ）
                save_conversation_log(channel_name, [("CEO", content), (agent["name"], clean_reply)])

                webhook_url = AGENT_WEBHOOKS.get(agent_key)
                if webhook_url:
                    await webhook_send(webhook_url, agent_key, clean_reply)
                else:
                    await message.channel.send(f"**{agent['name']}**\n{clean_reply}")

                if agent_key == "pm" and message.guild:
                    await handle_delegation(message.guild, reply)

                # エージェント間メッセージング（全エージェント共通）
                if message.guild and ('[SHARE:' in reply or '[MSG:' in reply):
                    await handle_agent_messaging(message.guild, agent_key, reply)

            except Exception as e:
                print(f"エラー: {e}")
                await message.channel.send(f"エラーが発生しました: {e}")

    await bot.process_commands(message)


bot.run(TOKEN)
