import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# CEOのユーザーID（このユーザー以外は無視）
CEO_ID = 1460895233213595851

# agent.mdを読み込む関数
def load_agent_prompt(agent_key):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_file = os.path.join(base_dir, "agents", agent_key, "agent.md")
    if os.path.exists(agent_file):
        with open(agent_file, "r", encoding="utf-8") as f:
            return f.read()
    return None

# エージェント定義（起動時にagent.mdを読み込む）
AGENT_KEYS = {
    "secretary": "秘書エージェント",
    "sales": "営業エージェント",
    "pm": "PMエージェント",
    "dev": "開発エージェント",
    "development": "開発エージェント",
    "marketing": "マーケティングエージェント",
}

AGENTS = {}

def load_all_agents():
    key_to_folder = {
        "secretary": "secretary",
        "sales": "sales",
        "pm": "pm",
        "dev": "development",
        "development": "development",
        "marketing": "marketing",
    }
    for key, folder in key_to_folder.items():
        prompt = load_agent_prompt(folder)
        if prompt:
            AGENTS[key] = {
                "name": AGENT_KEYS[key],
                "prompt": f"""あなたは以下の定義に従って動作するAIエージェントです。必ず日本語で応答してください。

## 応答スタイルの絶対ルール
- 基本は3行以内で端的に答える
- 「詳しく」「教えて」「説明して」「どうすれば」「提案して」などの言葉がある場合のみ詳しく答える
- 挨拶・確認・簡単な質問は1〜2文で返す
- 余計な前置き・まとめ・箇条書きの羅列は不要
- 本当に必要な情報だけを伝える

## エージェント定義
{prompt}"""
            }
            print(f"読み込み完了: {key} ({folder}/agent.md)")
        else:
            # agent.mdがない場合はフォールバック
            AGENTS[key] = {
                "name": AGENT_KEYS[key],
                "prompt": f"あなたはAI会社の{AGENT_KEYS[key]}です。簡潔で的確な日本語で応答してください。"
            }
            print(f"agent.md未検出、デフォルト使用: {key}")

def get_agent_by_channel(channel_name):
    for key in AGENTS:
        if key in channel_name:
            return key
    return "secretary"

@bot.event
async def on_ready():
    load_all_agents()
    print(f"Bot起動完了: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # CEO以外は無視
    if message.author.id != CEO_ID:
        return

    # !ping（動作確認）
    if message.content == "!ping":
        await message.channel.send("AI会社Bot 稼働中です！")
        return

    # Botへのメンションまたはチャンネル名にエージェント名が含まれる場合に応答
    is_mention = bot.user in message.mentions
    channel_name = message.channel.name if hasattr(message.channel, 'name') else ""
    is_agent_channel = any(key in channel_name for key in AGENTS)

    if is_mention or is_agent_channel:
        content = message.content
        content = content.replace(f"<@{bot.user.id}>", "")
        content = content.replace(f"<@!{bot.user.id}>", "")
        content = content.strip()
        if not content:
            await message.channel.send("何かご用件はありますか？")
            return

        agent_key = get_agent_by_channel(channel_name)
        agent = AGENTS[agent_key]

        async with message.channel.typing():
            try:
                response = claude.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=agent["prompt"],
                    messages=[{"role": "user", "content": content}]
                )
                reply = response.content[0].text
                await message.channel.send(f"**{agent['name']}**\n{reply}")
            except Exception as e:
                print(f"エラー: {e}")
                await message.channel.send(f"エラーが発生しました: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
