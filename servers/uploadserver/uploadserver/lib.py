import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dblib.main import DataBase
import random
import string
import requests


db = DataBase("data")

def get_size_file(file: bytes):
    data_size = len(file)
    mb_data_size = data_size / (1024 * 1024)
    return mb_data_size

def create_param(lengh: int) -> str:
    character = string.ascii_letters + string.digits

    param = ''.join(random.choice(character) for _ in range(lengh))
    return param


def send_video_server(param):
    global db
    data = db.get(param)
    response = requests.get(url=data["server"], params={"param": data["param"]}, stream=True)

def send_video_to_server(param, file):
    pass


print(create_param(32))