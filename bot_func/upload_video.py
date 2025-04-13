import requests
import base64

def upload_video(file, server, TOKEN):
    encode_data = base64.b64encode(file).decode('utf-8')
    data = {
        'file': encode_data,
        'TOKEN': TOKEN
    }
    response = requests.post(server + "upload-video/", json=data)
    if response.status_code == 200:
        content = response.json()
        return content.get("param")
    else:
        return False