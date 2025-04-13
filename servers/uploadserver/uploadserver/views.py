from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dblib.main import DataBase
import requests
import json
import base64
from uploadserver.lib import create_param
import sys



_db = DataBase("/path/to/folder/data")

def main(request):
    return HttpResponse("hello world")

@csrf_exempt
def test_url(request):
    param = request.GET.get('key')
    if param == "hi":
        return JsonResponse({"answer": "hello"})
    else:
        return JsonResponse({"error": request})

@csrf_exempt
def get_video(request):
    global _db
    param = request.GET.get('param')
    token = request.GET.get('TOKEN')
    video_data = _db.get(param)
    server_conf = _db.get("serverconf")

    if token == server_conf["TOKEN"]:
        host = video_data["host"]
        if host == "":
            return JsonResponse({"error": "host not found"})


        response = requests.get(f'{host}get-vid', params={'param': param}, stream=True)

        if response.status_code == 200:
            data = response.json()
            file = base64.b64decode(data.get('file'))
            if str(type(file))[8:-2] == 'bytes':
                data_send = {
                    'file': data.get('file')
                }
                return JsonResponse(data_send)
            else:
                return JsonResponse({"error": "Failed to retrieve video"}, status=response.status_code)
    else:
        return JsonResponse({"error": "token not found"})

@csrf_exempt
def upload_video(request):
    global _db
    data = json.loads(request.body)
    file = base64.b64decode(data.get('file'))
    size_file = (sys.getsizeof(file) / 1000000)
    if str(type(file))[8:-2] != 'bytes':
        return JsonResponse({"error": "file not found"})
    token = data.get('TOKEN')
    selected_host = ""
    server_data = _db.get("serverconf")
    if token == server_data["TOKEN"]:
        for server in server_data["servers"]:
            for key, value in server.items():
                if "freespace" in server[key] and server[key]["freespace"] > size_file:
                    selected_host = key
                    break
                else:
                    continue

        if selected_host == "":
            return JsonResponse({"error": "no host space"})
        file_sended = data.get('file')
        param = create_param(8).upper()
        sended_data = {
            'file': file_sended,
            'param': param
        }
        response = requests.post(selected_host + "/upload-vid", json=sended_data)

        if response.status_code == 200:
            _db.insert(param, {
                "filename": param,
                "size": size_file,
                "host": selected_host
            })
            j = -1
            for i in server_data["servers"]:
                j += 1
                for key, value in i.items():
                    if selected_host == key:
                        server_data["servers"][j][key]["freespace"] -= size_file
                        server_data["servers"][j][key]["usedspace"] += size_file
                        server_data["servers"][j][key]["params"].append(param)

            _db.update("serverconf", server_data)
            response = requests.get(selected_host + "initserver")
            return JsonResponse({"status": "ok", "param": param})
        else:
            return JsonResponse({"error": json.loads(response.content)})
    else:
        return JsonResponse({"error": "token not found or not verifyed"})

@csrf_exempt
def get_disk_data(request):
    global _db
    available_space = 0
    total_space = 0
    server_data = _db.get("serverconf")
    #return JsonResponse({"data": json.loads(request.body)})
    data = json.loads(request.body)
    #return JsonResponse(data)
    if data.get("TOKEN") == server_data["TOKEN"]:
        try:
            for i in server_data["servers"]:
                for key, value in i.items():
                    available_space += i[key]["freespace"]
                    total_space += i[key]["totalspace"]
            return JsonResponse({"totalspace": total_space, "freespace": available_space})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "token not found or not verified"}, status=403)


@csrf_exempt
def add_server(request):
    global _db
    data = json.loads(request.body)
    token = data.get('TOKEN')
    server_data = _db.get("serverconf")
    new_host = data.get('host')

    if token == server_data["TOKEN"]:
        try:
            response = requests.get(new_host + "initserver")
            #return JsonResponse({"data": response.json()})
            if response.status_code == 200:
                host_data = response.json()

                if host_data:
                    server_data["servers"].append({
                        new_host: {
                            "totalspace": host_data["diskdata"]["totalspace"],
                            "freespace": host_data["diskdata"]["freespace"],
                            "usedspace": host_data["diskdata"]["usedspace"],
                            "params": []
                        }
                    })
                    _db.update("serverconf", server_data)
                    return JsonResponse({"status": "ok", "message": "server added"})
                else:
                    return JsonResponse({"error": "diskdata not found"}, status=400)
            else:
                return JsonResponse({"error": "failed to initialize server", "error log": str(response.content)}, status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "token not found or not verified"}, status=403)


