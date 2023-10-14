from os import getenv
from dotenv import load_dotenv
from discord import Intents, Embed, utils, FFmpegPCMAudio, File
from discord.ext import commands
from discord.ext.commands import Context
import json
import re

from time import sleep
import random

from meme_gen import MemeGenerator
from memes import Memes

import requests
from pytube import YouTube

from datetime import date

import logging

load_dotenv("a.env")
TOKEN = getenv("DISCORD_TOKEN")
ADMIN_ID = getenv("DISCORD_ADMIN_ID")
CRON_ID = getenv("CRON_ID")

# imgflip
GENUSERNAME = getenv("GENUSERNAME")
GENPASSWORD = getenv("GENPASSWORD")

# reddit
MCID = getenv("MCLIENT_ID")
MCSECRET =  getenv("MCLIENT_SECRET")
MUSER = getenv("MUSERNAME")
MPASSWORD = getenv("MPASSWORD")

# files
fpdes = "description.txt"
fsubs = "subs.json"
ferrors = "discord.log"

# creating bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

#log
handler = logging.FileHandler(filename=ferrors, encoding='utf-8', mode='w')


#------------------ starter ------------------

@bot.event
async def on_ready():
    print("bot is ready")
    await bot.tree.sync()


# ------------- meme generator ---------------
meme_generator = MemeGenerator(GENUSERNAME, GENPASSWORD)

@bot.hybrid_command(name="list_memes", brief="give you list of templates")
async def list_memes(ctx: Context, n=25) -> None:
    if n>50 or n<1:
        await ctx.send("you are out of range")
        return
    meme_list = meme_generator.list_memes(n)
    embed = Embed()
    embed.description = meme_list
    await ctx.send(embed=embed)


@bot.hybrid_command(name="make_meme", brief="make meme from template")
async def make_meme(ctx: Context, template_id=102156234, top_text=" ", bottom_text=" ") -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    await ctx.send(meme_url)


# --------------- MEMES ----------------
memes = Memes(MUSER,MPASSWORD,MCID,MCSECRET)

# channel subs
@bot.hybrid_command(name="sub", brief="make subscription for subreddit")
async def sub(ctx, subreddit,channel_name=None):
    if not memes.sub_exists(subreddit):
        await ctx.send("subreddit does not exist")
        return
    if channel_name is None:
        channel = ctx.channel
    else:
        channel = utils.get(ctx.guild.channels, name=channel_name)
    with open(fsubs,"r") as f:
        allsubs = json.load(f)
    if str(ctx.guild.id) in allsubs:
        if str(channel.id) in allsubs[str(ctx.guild.id)]:
            allsubs[str(ctx.guild.id)][str(channel.id)].append(subreddit)
        else:
            allsubs[str(ctx.guild.id)][str(channel.id)] = [subreddit]
    else:
        allsubs[str(ctx.guild.id)] = {str(channel.id):None}
        allsubs[str(ctx.guild.id)][str(channel.id)] = [subreddit]
    with open(fsubs, "w") as f:
            json.dump(allsubs, f)
            await ctx.send("subscribed")


@bot.hybrid_command(name="unsub", brief="delete subscription")
async def unsub(ctx, subreddit,channel_name=None):
    if channel_name is None:
        channel = ctx.channel
    else:
        channel = utils.get(ctx.guild.channels, name=channel_name)
    with open(fsubs,"r") as f:
        allsubs = json.load(f)
    try:
        allsubs[str(ctx.guild.id)][str(channel.id)]
    except KeyError:
        await ctx.send("this subscription does not exist")
        return
    if subreddit in allsubs[str(ctx.guild.id)][str(channel.id)]:
        allsubs[str(ctx.guild.id)][str(channel.id)].remove(subreddit)
    else:
        await ctx.send("this subscription does not exist")
        return
    with open(fsubs, "w") as f:
            json.dump(allsubs, f)
            await ctx.send("unsubscribed")

@bot.hybrid_command(name="subs", brief="list of subscriptions")
async def subs(ctx):
    with open(fsubs,"r") as f:
        allsubs = json.load(f)
    try:
        allsubs[str(ctx.guild.id)][str(ctx.channel.id)]
    except KeyError:
        await ctx.send("you have got no subscription for this channel")
        return
    if allsubs[str(ctx.guild.id)][str(ctx.channel.id)] == []:
        await ctx.send("you have got no subscription for this channel")
        return
    embed = Embed()
    embed.title = "Your subsciptions:"
    embed.description = ""
    for sub in allsubs[str(ctx.guild.id)][str(ctx.channel.id)]:
        embed.description += "\n"+sub
    await ctx.send(embed=embed)

@bot.command(name="cron", brief="for admin")
async def cron(ctx):
    if int(ADMIN_ID) != ctx.author.id and int(CRON_ID) != ctx.author.id:
        return
    with open(fsubs,"r") as f:
        allsubs = json.load(f)
    for guild_id in allsubs.keys():
        guild = await bot.fetch_guild(guild_id)
        if not guild:
            pass
        else:
            for channel_id in allsubs[guild_id].keys():
                channel = await guild.fetch_channel(int(channel_id))
                for subreddit in allsubs[guild_id][channel_id]:
                    meme = memes.meme(subreddit)
                    if meme == None:
                        await channel.send("subreddit does not exist")
                    else:
                        embed = Embed()
                        embed.title = "**"+subreddit+"**"
                        embed.description = meme.split("$")[0]
                        embed.set_image(url=meme.split("$")[1])
                        await ctx.send(embed=embed)


@bot.hybrid_command(name="meme", brief="show you n memes")
async def meme(ctx: Context,subreddit: str, n = 1) -> None:
    if n>50 or n<1:
        await ctx.send("you are out of range")
        return
    embed = Embed()
    embed.title = "**"+subreddit+"**"
    for i in range(n):
        meme = memes.meme(subreddit)
        if meme == None:
            embed.description = "subreddit does not exist"
            await ctx.send(embed=embed)
            return
        embed.description = meme.split("$")[0]
        embed.set_image(url=meme.split("$")[1])
        await ctx.send(embed=embed)
        sleep(1)    



# ------------- MUSIC -------------
class music_bot():
    def __init__(self):
        self.vc = None
        self.channel = None
        self.playing = None
        self.queue = []

servers = {}


# helper functions
def linkEdit(url):
    yturl = "https://www.youtube.com/watch?"
    code = re.search("v=[0-9A-Za-z_-]{11}",url)
    if code:
        url = yturl + code.group(0)
        response = requests.get(url)
        if response.status_code == 200:
            return url
    return None

def checking(ctx):
    if not str(ctx.guild.id) in servers:
        return None
    mb = servers[str(ctx.guild.id)]
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return None
    if channel is None or mb.channel is not channel:
        return None
    return mb


def play_next(server_id):
    mb = servers[server_id]
    if len(mb.queue)>0:
        mb.playing = mb.queue[0]
        try:
            yt = YouTube(mb.playing)
            if yt.length > 3600: 
                mb.queue.pop(0)
                play_next(server_id)
                return
            video = yt.streams.get_audio_only()
            video.download(filename=server_id+".mp3")
        except Exception:
            pass
        mb.queue.pop(0)
        mb.vc.play(FFmpegPCMAudio(server_id+".mp3"), after=lambda e: play_next(server_id))
    else:
        mb.playing = None
    servers[server_id] = mb



# music bot functions
@bot.hybrid_command(name="play", aliases=["p"], brief="start play url")
async def play(ctx, url):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("you are not in the voice channel")
        return
    if not str(ctx.guild.id) in servers:
        servers[str(ctx.guild.id)] = music_bot()
    mb = servers[str(ctx.guild.id)]
    if mb.vc is None or not mb.vc.is_connected:
        mb.channel = channel
        mb.vc = await mb.channel.connect()
    elif mb.channel is not channel:
        await ctx.send("you are not in the voice channel, where I am")
        return
    url = linkEdit(url)
    if url:
        yt = YouTube(url)
        await ctx.send("**"+yt.title + "** from **"+yt.author+"** added")
        mb.queue.append(url)
        servers[str(ctx.guild.id)] = mb
        if mb.vc.is_paused():
           mb.vc.resume() 
        if not mb.vc.is_playing():
            play_next(str(ctx.guild.id))
    else:
        await ctx.send("bad link")

#some people forgot resume command, so p will work as resume
@play.error
async def play_error(ctx: Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await resume(ctx)


@bot.hybrid_command(name="skip", aliases=["s"], brief="skip playing")
async def skip(ctx):
    mb = checking(ctx)
    if not mb:
        await ctx.send("either you or bot is disconnected")
        return
    channel = ctx.author.voice.channel
    if channel is None or mb.channel is not channel:
        await ctx.send("you are not on the same voice channel")
    if mb.vc.is_playing():
        mb.vc.stop()
        await ctx.send("skipped")


    
@bot.hybrid_command(name="pause")
async def pause(ctx):
    mb = checking(ctx)
    if not mb:
        await ctx.send("either you or bot is disconnected")
        return
    mb.vc.pause()
    servers[str(ctx.guild.id)] = mb
    await ctx.send("paused")
        

@bot.hybrid_command(name="resume")
async def resume(ctx):
    mb = checking(ctx)
    if not mb:
        await ctx.send("either you or bot is disconnected")
        return
    if mb.vc.is_paused():
        mb.vc.resume()
        servers[str(ctx.guild.id)] = mb
        await ctx.send("resumed")
        

@bot.hybrid_command(name="leave", aliases=["l"], brief="leave voice chat")
async def leave(ctx):
    mb = checking(ctx)
    if not mb:
        await ctx.send("either you or bot is disconnected")
        return
    mb.queue = []
    mb.vc.stop()
    await mb.vc.disconnect()
    mb.channel = None
    mb.vc = None
    mb.playing = None
    servers[str(ctx.guild.id)] = mb
    await ctx.send("bot left")



@bot.hybrid_command(name="queue", aliases=["q"], brief="send queue of music")
async def queue(ctx):
    mb = checking(ctx)
    if not mb:
        await ctx.send("either you or bot is disconnected")
        return
    embed = Embed()
    embed.title = "**Songs:**"
    txt = ""
    if mb.vc.is_playing() or mb.vc.is_paused():
        try:
            yt = YouTube(mb.playing)
            txt = "curently playing: [" + yt.title + " -- "+yt.author+"]("+mb.playing+")\n"
        except Exception:
            await ctx.send("fuck you pytube")
    if mb.queue:
        i = 1
        for song in mb.queue:
            try:# random pytube errors
                yt = YouTube(song)
                txt = txt + str(i)+".  ["+ yt.title+" -- "+yt.author+"]("+song+")\n"
                i += 1
            except Exception:
                await ctx.send("fuck you pytube")
    embed.description = txt
    await ctx.send(embed=embed)
        

# -------------- SPECIAL --------------
@bot.command(name="dt", brief="create thread with todays date as a name")
async def dt(ctx: Context) -> None:
    today = date.today().strftime("%d. %m. %Y")
    await ctx.message.create_thread(name=today)
    
    
    
# --------------- HELP ---------------
@bot.hybrid_command(name="h", brief="better help")
async def h(ctx: Context) -> None:
    embed = Embed()
    embed.title = "**"+bot.user.name+" !h**"
    with open(fpdes) as f:
        embed.description = f.read()
    await ctx.send(embed=embed)


@bot.command(name="log", brief="for admin")
async def log(ctx: Context) -> None:
    if int(ADMIN_ID) != ctx.author.id:
        return
    await ctx.send(file=File("discord.log"))


@bot.event
async def on_command_error(ctx: Context, error):
    print(error)
    await ctx.send(error)

bot.run(TOKEN, log_handler=handler)