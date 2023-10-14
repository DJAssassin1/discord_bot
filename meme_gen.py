import requests


# imgflip
IMGFLIP_API_URL = "https://api.imgflip.com"

class MemeGenerator:
    def __init__(self, username : str, password : str) -> None:
        self.username = username
        self.password = password

    def list_memes(self, n : int) -> str:
        response = requests.get(IMGFLIP_API_URL+"/get_memes")
        memes = (response.json()["data"])["memes"]
        result = ""
        for meme in memes[:(n-1)]:
            whitespace = (12-len(meme["id"]))*"."*2+meme["name"]
            add = meme["id"]+whitespace+"  [here]("+meme["url"]+")\n"
            result += add
        return result

    def make_meme(
        self, template_id: int, top_text: str, bottom_text: str
    ) -> str:
        data = {"template_id": template_id,
                "username": self.username,
                "password": self.password,
                "text0": top_text,
                "text1": bottom_text
                }
        response = requests.post(IMGFLIP_API_URL+"/caption_image", data=data)
        if response.json()["success"]:
            return (response.json()["data"])["url"]
        else:
            return response.json()["error_message"]