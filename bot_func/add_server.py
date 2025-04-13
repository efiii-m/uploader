import requests

def add_server(server, url, TOKEN):
    data = {
        "host": url,
        "TOKEN": TOKEN
        }
    response = requests.post(server + "add-server/", json=data)
    if response.status_code == 200:
        return True
    else:
        return response.content