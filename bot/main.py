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

# エージェント定義
AGENTS = {
    "secretary": {
        "name": "秘書エージェント",
        "prompt": "あなたはAI会社のCEO専属秘書です。タスク管理・情報整理・会議要約を担当します。簡潔で的確な日本語で応答してください。"
    },
    "sales": {
        "name": "営業エージェント",
        "prompt": "あなたはAI会社の営業エージェントです。クライアント開拓・Webサイト分析・アウトリーチを担当します。簡潔で的確な日本語で応答してください。"
    },
    "pm": {
        "name": "PMエージェント",
        "prompt": "あなたはAI会社のプロジェクトマネージャーです。プロジェクト管理・タスク割り当て・進捗追跡を担当します。簡潔で的確な日本語で応答してください。"
    },
    "dev": {
        "name": "開発エージェント",
        "prompt": "あなたはAI会社の開発エージェントです。Webサイト制作・モックアップ生成・コーディングを担当します。簡潔で的確な日本語で応答してください。"
    },
    "marketing": {
        "name": "マーケティングエージェント",
        "prompt": "あなたはAI会社のマーケティングエージェントです。SNSコンテンツ制作・ブランド管理・リード獲得を担当します。簡潔で的確な日本語で応答してください。"
    },
}

def get_agent_by_channel(channel_name):
    for key in AGENTS:
        if key in channel_name:
            return key
    return "secretary"  # デフォルトは秘書

@bot.event
async def on_ready():
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
        # メンション部分を除いたテキストを取得（<@ID>と<@!ID>両方に対応）
        content = message.content
        content = content.replace(f"<@{bot.user.id}>", "")
        content = content.replace(f"<@!{bot.user.id}>", "")
        content = content.strip()
        if not content:
            await message.channel.send("何かご用件はありますか？")
            return

        # エージェントを選択
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
