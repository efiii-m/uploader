from flask import Flask, request, jsonify
from dblib.main import DataBase
from diskusage import get_spaces
import base64
import sys
class MyApp:
    def __init__(self, host: str, port: int) -> None:
        self._app = Flask(__name__)
        self._host = host
        self._port = port
        self._db = DataBase("/path/to/folder/data")
        self.initalize()

    def initalize(self):
        @self._app.route('/', methods=["GET"])
        def main():
            return "hello world"

        @self._app.route('/test', methods=["GET"])
        def test():
            key = request.args.get('key')
            if key == "hi":
                return jsonify({"answer": "hello"})

        @self._app.route('/get-vid', methods=["GET"])
        def get_vid():
            param = request.args.get("param")
            data = self._db.get("data")
            if param in data["params"]:
                try:
                    with open(f"/main path of project/videos/{param}" + ".mp4", "rb") as f:
                        content = f.read()
                        file = base64.b64encode(content).decode('utf-8')
                        data = {
                            'file': file,
                            }
                        return jsonify(data)
                except FileNotFoundError:
                    return jsonify({"error": "File not found"}), 404
            return jsonify({"error": "Invalid parameter"}), 403

        @self._app.route('/upload-vid', methods=["POST"])
        def upload_vid():
            data = request.get_json()
            conf = self._db.get('data')
            param = data['param']
            file = base64.b64decode(data['file'])
            file_size = sys.getsizeof(file) / 1000000
            try:
                with open("/main path of project/videos/" + param + ".mp4", "wb") as f:
                    f.write(file)
                conf["params"].append(param)
                conf["disk"]["freespace"] -= file_size
                conf["disk"]["usedspace"] += file_size
                self._db.update("data", conf)
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self._app.route('/initserver', methods=["GET"])
        def init_server():
            try:
                data = get_spaces()
                #return jsonify(data)
                serverdata = self._db.get("data")
                #return jsonify(serverdata)
                serverdata["disk"]["freespace"] = data["freespace"]
                serverdata["disk"]["totalspace"] = data["totalspace"]
                serverdata["disk"]["usedspace"] = data["usedspace"]
                self._db.update("data", serverdata)
                #return jsonify(serverdata)
                return jsonify({
                    "diskdata": data,
                    "status": "ok, all down"
                }), 200
            except Exception as e:
                return jsonify({
                    "error": str(e)
                    })


    def run(self):
        self._app.run(self._host, self._port)

