# ==============================================================================
# filename  : Music_bot.py
# author    : 김현우
# date      : 2025-04-23
#
# description :
#     디스코드 음성 채널에서 유튜브 음악을 재생하는 봇입니다.
#     사용자의 음성 채널에 접속하면 음악을 검색하고 재생할 수 있습니다.
#     
#     초대 링크: https://discord.com/oauth2/authorize?client_id=1364567374203981844&permissions=8&integration_type=0&scope=bot
# 
#     명령어 사용법:
##    !help1 - 도움말 출력
#     !play [검색어] 또는 !p [검색어] - 유튜브에서 음악 검색 후 재생
#     !pause - 음악 일시 정지
#     !resume - 음악 재개
#     !skip - 다음 곡으로 스킵
#     !queue_list - 대기열 확인
#     !stop - 음악 중지 및 방식 통을 퇴장
#     !loop - 루프 모드 토그런
#     !status - 상태 메시지 출력
#     !set_channel [channel_name]: 특정 채널에 봇을 설정합니다.
#
#
# organization : 
# repository : https://github.com/rlagusdn04/python-workspace/tree/main/bot
# 
# @This file was written by rlagudn04
# @version 1.0
# ==============================================================================

import discord
from discord.ext import commands
import yt_dlp
import asyncio

# 토큰 파일에서 디스코드 방식 토큰 읽기
def load_token_from_file(path="token.txt"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❗ token.txt 파일이 없습니다.")
        return None

# 방식 기본 설정
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
loop_mode = False  # 루프 모드 플래그

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 512k'
}

# 봇의 출력 채널을 저장할 전역 변수
output_channels = {}  # {guild_id: channel_id}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} 방식이 준비되었습니다.')

@bot.command()
async def play(ctx, *, search: str):
    if not await check_channel(ctx):
        return

    if not ctx.author.voice:
        await ctx.send("🎧 먼저 음성 채널에 접속해 주세요.")
        return

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        url = info['url']
        title = info['title']

    queue.append((url, title))
    await ctx.send(f"🎵 **{title}** 을(를) 대기열에 추가했습니다.")

    if not vc:
        vc = await channel.connect()

    if not vc.is_playing():
        await play_next(ctx.guild)

@bot.command()
async def p(ctx, *, search: str):
    await play(ctx, search=search)

async def play_next(guild):
    vc = discord.utils.get(bot.voice_clients, guild=guild)
    if vc and (queue or loop_mode):
        if loop_mode and not queue:
            queue.append((vc.source.url, getattr(vc.source, "title", "Unknown")))

        url, title = queue.pop(0)
        await send_now_playing(guild, title)

        def after_playing(error):
            if error:
                print(f"❌ 재생 오류: {error}")
            fut = asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"❌ 다음 곡 재생 실패: {e}")

        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=after_playing)

async def send_now_playing(guild, title):
    if guild.id in output_channels:
        channel = guild.get_channel(output_channels[guild.id])
        if channel:
            await channel.send(f"🎶 지금 재생 중: **{title}**")
            return
    
    # 설정된 채널이 없거나 찾을 수 없는 경우 기본 동작 (일반 채널에 전송)
    for channel in guild.text_channels:
        if "일반" in channel.name:
            await channel.send(f"🎶 지금 재생 중: **{title}**")
            return

@bot.command()
async def loop(ctx):
    if not await check_channel(ctx):
        return
    global loop_mode
    loop_mode = not loop_mode
    status = "🔁 루프 모드 활성화." if loop_mode else "➡️ 루프 모드 비활성화."
    await ctx.send(status)

@bot.command()
async def pause(ctx):
    if not await check_channel(ctx):
        return
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ 음악 일시 정지됨.")

@bot.command()
async def resume(ctx):
    if not await check_channel(ctx):
        return
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ 음악 다시 재생됨.")

@bot.command()
async def skip(ctx):
    if not await check_channel(ctx):
        return
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ 다음 곡으로 넘어갑니다.")

@bot.command()
async def queue_list(ctx):
    if not await check_channel(ctx):
        return
    if ctx.guild.id in output_channels:
        channel = ctx.guild.get_channel(output_channels[ctx.guild.id])
        if channel and channel.id != ctx.channel.id:
            await ctx.send(f"❗ 이 명령어는 '{channel.name}' 채널에서만 사용할 수 있습니다.")
            return

    if queue:
        msg = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queue)])
        await ctx.send(f"📋 대기열:\n{msg}")
    else:
        await ctx.send("�� 대기열이 비어 있습니다.")

@bot.command()
async def stop(ctx):
    if not await check_channel(ctx):
        return
    if ctx.voice_client:
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 음악 종료 및 음성 채널 퇴장.")

@bot.command()
async def status(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send("⚠️ 김현우님의 코멘터가 끝났습니다.")

@bot.command()
async def help1(ctx):
    help_text = """
🎵 **음악 봇 명령어 목록** 🎵

• `!play [검색어]` 또는 `!p [검색어]` - 유튜브에서 음악 검색 후 재생
• `!pause` - 음악 일시 정지
• `!resume` - 음악 재개
• `!skip` - 다음 곡으로 스킵
• `!queue_list` - 대기열 확인
• `!stop` - 음악 중지 및 봇 퇴장
• `!loop` - 루프 모드 토글
• `!status` - 상태 메시지 출력
• `!set_channel [채널명]` - 특정 채널에 봇을 설정
• `!help` - 이 도움말 메시지 표시
    """
    await ctx.send(help_text)

@bot.command()
async def set_channel(ctx, channel_name: str):
    # 입력된 이름의 텍스트 채널 찾기
    channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
    if channel:
        # 해당 서버의 출력 채널 설정
        output_channels[ctx.guild.id] = channel.id
        await ctx.send(f"✅ 봇의 출력 채널이 '{channel_name}'(으)로 설정되었습니다.")
    else:
        await ctx.send(f"❌ '{channel_name}' 채널을 찾을 수 없습니다.")

async def check_channel(ctx):
    if ctx.guild.id in output_channels:
        channel = ctx.guild.get_channel(output_channels[ctx.guild.id])
        if channel and channel.id != ctx.channel.id:
            await ctx.send(f"❗ 이 명령어는 '{channel.name}' 채널에서만 사용할 수 있습니다.")
            return False
    return True

if __name__ == "__main__":
    TOKEN = load_token_from_file()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❗ 방식 토큰을 불러올 수 없어 실행을 종료합니다.")