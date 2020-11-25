import asyncio
import youtube_dl
import discord
import random
import os

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0" # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if "entries" in data:
            # Take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def music(self):
    self.playlist = []
    with open("./static/playlist.txt") as fin:
        fin.readline() # Header
        x = fin.readline()
        while x:
            k = x.split("\t")
            if len(k[1]) > 0:
                self.playlist.append(k)
            x = fin.readline()

    self.vc = self.get_channel(764193661461200926)
    self.voice = await self.vc.connect()

    await self.guilds[0].change_voice_state(channel=self.vc, self_deaf=True)

    print("Connected to voice channel!")

    asyncio.ensure_future(self.play_music())


async def play_music(self):
    while True:
        if not self.voice.is_playing():
            while True:
                url = random.choice(self.playlist)[1].strip()
                if url == "":
                    continue
                print(url)
                print(repr(url))
                os.chdir("./temp")
                try:
                    source = await YTDLSource.from_url(url, loop=False, stream=False)
                    self.voice.play(source)
                    os.chdir(os.pardir)
                    break
                except:
                    os.chdir(os.pardir)

        await asyncio.sleep(10)