import requests
import base64

def get_video(param: str, server: str, TOKEN: str):
    try:
        response = requests.get(server + "get-video/", params={"param": param, "TOKEN": TOKEN}, stream=True)
        data = response.json()
        file = base64.b64decode(data.get('file'))

        return file
    except Exception as e:
        return str(e)
