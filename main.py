import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
import urllib.parse, urllib.request, re

def run_bot():
    TOKEN = 'MTMwNjA3NjY0OTMzNDUwOTY3OA.GiyTxI.RmVjx2ICd9PyPj3Q3_zE2I0dLDPOieOaNxCf7M'
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="!", intents=intents)

    queues = {}
    voice_clients = {}
    youtube_base_url = 'https://www.youtube.com/'
    youtube_results_url = youtube_base_url + 'results?'
    youtube_watch_url = youtube_base_url + 'watch?v='
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    # Đặt giá trị âm lượng mặc định
    current_volume = 1.0
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': f'-vn -filter:a "volume={current_volume}"'
    }

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link=link)

    @client.command(name="play", help="Phát nhạc")
    async def play(ctx, *, link):
        if ctx.author.voice is None:
            await ctx.send("Bạn cần tham gia vào một kênh voice trước!")
            return

        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[ctx.guild.id] = voice_client
            await asyncio.sleep(1)  # Thời gian chờ sau khi kết nối
        except discord.ClientException:
            voice_client = ctx.voice_client

        try:
            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({'search_query': link})
                content = urllib.request.urlopen(youtube_results_url + query_string)
                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
                link = youtube_watch_url + search_results[0]

            data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(link, download=False))
            song = data['url']
            name_music = data['title']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            await ctx.send(f'Đang phát: {name_music}')
            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        except Exception as e:
            print(e)

    @client.command(name="pause", help="Tạm dừng phát nhạc")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

    @client.command(name="resume", help="Tiếp tục phát nhạc")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    @client.command(name="stop", help="Dừng nhạc đang phát")
    async def stop(ctx):
        try:
            voice_client = ctx.voice_client
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
        except Exception as e:
            print(e)
    @client.command(name='bo', help='Vui vậy thôi nhưng bố dặn con này')
    async def bo(ctx):
        if ctx.author.voice is None:
            await ctx.send("Bạn cần tham gia vào một kênh voice trước!")
            return

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.voice_client

        file_path = "meme/bo.mp3"

        # Phát nhạc
        try:
            source = discord.FFmpegPCMAudio(file_path)
            voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send(f'Vui vậy thôi nhưng bố dặn con này ')
        except Exception as e:
            await ctx.send("Có lỗi xảy ra")
            print(e)
    @client.command(name='ditme', help='BOOMAN')
    async def dm(ctx):
        if ctx.author.voice is None:
            await ctx.send("Bạn cần tham gia vào một kênh voice trước!")
            return

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.voice_client

        file_path = "meme/ditme.mp3"

        # Phát nhạc
        try:
            source = discord.FFmpegPCMAudio(file_path)
            voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send(f'CDMM')
        except Exception as e:
            await ctx.send("Có lỗi xảy ra")
            print(e)


    @client.command(name='kheu', help='Xin donate')
    async def send_image(ctx):
        # Đường dẫn tới ảnh muốn gửi
        image_path = "image/kheu.jpg"  # Đổi thành đường dẫn file ảnh của bạn
        # Gửi ảnh
        try:
            with open(image_path, "rb") as image:
                await ctx.send("Lạy ông đi qua,\nLạy bà đi lại,\nCho con 5k duy trì client")
                await ctx.send(file=discord.File(image, filename="image.png"))

        except FileNotFoundError:
            await ctx.send("Image not found! Please check the path.")\


        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.voice_client

        file_path = "meme/kheu.mp3"

        # Phát nhạc
        try:
            source = discord.FFmpegPCMAudio(file_path)
            voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        except Exception as e:
            await ctx.send("Có lỗi xảy ra")
            print(e)

    @client.command(name="volume", help="Tăng giảm âm lượng, min: 0.1 max: 2.0")
    async def volume(ctx, vol: float):
        global current_volume
        if 0.1 <= vol <= 2.0:  # Giới hạn từ 10% đến 200%
            current_volume = vol
            ffmpeg_options['options'] = f'-vn -filter:a "volume={current_volume}"'
            await ctx.send(f"Đã đặt âm lượng thành {int(current_volume * 100)}%")
        else:
            await ctx.send("Vui lòng chọn mức âm lượng từ 0.1 đến 2.0")

    client.run(TOKEN)

if __name__ == '__main__':
    run_bot()
