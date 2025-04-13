import requests

def get_disk_data(server, token):
    response = requests.post(server + "get-disk-data/", json={"TOKEN": token})
    try:
        data = response.json()
        return {
            "totalspace": data["totalspace"],
            "freespace": data["freespace"]
        }
    except:
        return response.json()