import discord
from discord.ext import commands
import yt_dlp
import asyncio

# ─────────────────────────────────────────
# 토큰 파일에서 디스코드 봇 토큰 읽기
# ─────────────────────────────────────────
def load_token_from_file(path="token.txt"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❗ token.txt 파일이 없습니다.")
        return None

# ─────────────────────────────────────────
# 봇 기본 설정
# ─────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 512k'
}

# ─────────────────────────────────────────
# 이벤트
# ─────────────────────────────────────────
@bot.event
async def on_ready():
    print(f'✅ {bot.user} 봇이 준비되었습니다.')

# ─────────────────────────────────────────
# 명령어: 재생
# ─────────────────────────────────────────
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("🎙️ 먼저 음성 채널에 접속해 주세요.")
        return

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    # YouTube 검색
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

# ─────────────────────────────────────────
# 다음 곡 재생
# ─────────────────────────────────────────
async def play_next(guild):
    vc = discord.utils.get(bot.voice_clients, guild=guild)
    if queue and vc:
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

# ─────────────────────────────────────────
# 현재 재생 곡 출력
# ─────────────────────────────────────────
async def send_now_playing(guild, title):
    for channel in guild.text_channels:
        if "일반" in channel.name:
            await channel.send(f"🎶 지금 재생 중: **{title}**")
            return

# ─────────────────────────────────────────
# 재생 컨트롤 명령어
# ─────────────────────────────────────────
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ 음악 일시 정지됨.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ 음악 다시 재생됨.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ 다음 곡으로 넘어갑니다.")

@bot.command()
async def queue_list(ctx):
    if queue:
        msg = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queue)])
        await ctx.send(f"📃 대기열:\n{msg}")
    else:
        await ctx.send("📭 대기열이 비어 있습니다.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 음악 종료 및 음성 채널 퇴장.")

@bot.command()
async def status(ctx):
    await ctx.send("⚠️ 김현우님의 컴퓨터가 꺼져있습니다.")

# ─────────────────────────────────────────
# 실행
# ─────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = load_token_from_file()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❗ 봇 토큰을 불러올 수 없어 실행을 종료합니다.")
