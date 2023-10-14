# Discord_bot

## update

every function now works with /...

## Functions

### MemeGenerator

This part is created thanks to the [ImgFlip](https://imgflip.com/api) API. It has 2 functions:
 - !list_memes "x" - *gives a list of x meme templates, where x is max 50*
 - !make_meme "template id" "top text" "bottom text" - *makes a meme from a template*

### Memes

This part is created thanks to the [PRAW](https://praw.readthedocs.io/en/stable/index.html). It is divided into two parts:

For users:
 - !meme "subreddit" ["n"] - sends n uplouds from a subreddit

For channels:
In this part bot will send a meme from subcribed subreddits once in a while
 - !subs - sends your subscriptions for this channel
 - !sub "subreddit" ["channel"] - adds a choosen subreddit
 - !unsub "subreddit" ["channel"] - removes a choosen subreddit

### Music bot

 - !p[lay] "yt_link" - adds a song to the queue
 - !q[ueue] - sends a queue of songs
 - !s[kip] - skips a song
 - !l[eave] - leaves voice chat
 - !stop - stops the music
 - !resume - starts the music

### Special

I created this functions especially for my personal use.
 - !dt - creates a new thread with current date

## future functions

 - some games - quiz, hangman, ...
 - (behave similar in DMs)

## libraries

 - [discord.py](https://discordpy.readthedocs.io/en/stable/index.html)
 - dotenv
 - [praw](https://praw.readthedocs.io/en/stable/index.html)
 - pytube
 - ffmpeg

## APIs

 - Discord
 - imgflip
 - Reddit

## start

create account on Discord, Reddit and imgflip. Create bot on https://discord.com/developers. Download the libraries. Clone this project. Create file in it named a.env and fill it with this:

DISCORD_TOKEN=token for your bot
GENUSERNAME=imgflip
GENPASSWORD=imgflip
MCLIENT_ID=reddit api id
MCLIENT_SECRET=reddit api secret code
MUSERNAME=username for reddit
MPASSWORD=password for reddit
DISCORD_ADMIN_ID=your id
CRON_ID=second bot id
