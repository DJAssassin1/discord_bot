import praw
from prawcore import NotFound

class Memes:
    def __init__(self, username, password, cID, cSecret) -> None:
        self.reddit = praw.Reddit(username=username,
                                  password=password,
                                  client_id=cID,
                                  client_secret=cSecret,
                                  user_agent="pls kill me",
                                  check_for_async=False)
    
    def meme(self, subname: str):
        subreddit = self.sub_exists(subname)
        if not subreddit:
            return None
        meme = subreddit.random()
        if meme is None:
            meme = subreddit.hot(limit=1)
        return meme.author.name+": "+meme.title+"$"+meme.url
    
    def sub_exists(self, subname: str):
        try:
            sub = self.reddit.subreddit(subname)
            sub.random()
            return sub
        except NotFound:
            return None