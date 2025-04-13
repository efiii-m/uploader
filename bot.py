from telebot import TeleBot
from dblib.main import DataBase
from bot_func.murkups import allow_as_admin, wellcome_murk, admin_panel, join_channels
from bot_func.get_video import get_video
from bot_func.upload_video import upload_video
from bot_func.get_diskdata import get_disk_data
from bot_func.add_server import add_server
from time import sleep
import requests
import sys

class Bot:
    def __init__(self, TOKEN: str):
        self._apitoken = TOKEN
        self._bot = TeleBot(TOKEN)
        self._db = DataBase("/path/to/folder/data")
        data = self._db.get("data")
        self._token = data["TOKEN"]
        del data
        self._server = "http://127.0.0.1:8000/xyz-r/"
        self._message_id = 0
        self.initalaize()

    def initalaize(self):
        @self._bot.message_handler(func=lambda message: message.text.startswith('/start'))
        def start_bot(message):
            try:
                video_parametr = message.text.split(' ', 1)
                video_parametr = video_parametr[1] if len(video_parametr) > 1 else None

                if video_parametr != None:
                    if self.check_admin(message.chat.id):
                        self.send_video_to_user(message.chat.id, video_parametr)
                    else:
                        channels = self._db.get("channels")

                        user_stat = self.check_member(message.chat.id)
                        if user_stat == True:
                            self.send_video_to_user(message.chat.id, video_parametr)
                        else:
                            send = self._bot.send_message(message.chat.id, "لطفا در چنل های اسپانسر ربات عضو بشید", reply_markup=join_channels(channels["channels"], video_parametr))
                            self._message_id = send.id

                else:
                    self._bot.send_message(message.chat.id, "به ربات آپلودر مستر خوش آمدید\nاز ربات لذت ببرید!")
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")
            
        
        @self._bot.message_handler(commands=["login"])
        def login(message):
            self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید.", reply_markup=wellcome_murk("ورود به ادمین", "login"))
        
        @self._bot.message_handler(commands=["uploadvideo"])
        def upload_vid(message):
            try:
                if self.check_admin(message.chat.id):
                    self._bot.send_photo(message.chat.id, "hiii.jpg", "")
                    self._bot.send_message(message.chat.id, "لطفا فایل ویدیویی رو بفرستید")
                else:
                    self._bot.send_message(message.chat.id, "شما دسترسی ادمین ندارید", reply_markup=wellcome_murk("ورود به ادمین", "login"))
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")


        @self._bot.message_handler(func=lambda message: message.text.startswith('https://drive.google.com/'))
        def upload_handler(message):
            
            if self.check_admin(message.chat.id):
                try:
                    url = (message.text.split('/'))[-2] if len((message.text.split('/'))[-2]) == 33 else None
                    if url != None:
                        response = requests.get(f"https://drive.google.com/uc?id={url}&export=download", stream=True, allow_redirects=True)
                        send = upload_video(response.content, self._server, TOKEN=self._token)
                    else:
                        self._bot.send_message(message.chat.id, "آی دی فایل معتبر نیست")
                    send = upload_video(response.content, self._server, TOKEN=self._token)
                    if send:
                        data = self._db.get("data")
                        self._bot.send_message(message.chat.id, f"ویدئو آپلود شد، لینک ویدئو:\nhttps://t.me/{data['bot-username']}?start={send}")
                    else:
                        self._bot.send_message(message.chat.id, f"error while sending file\n{send}")
                except Exception as e:
                    admins = self._db.get("admins")
                    self._bot.send_message(admins["main-admin"], f"error\n{str(e)}")
            else:
                self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید.", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))

        @self._bot.message_handler(commands=['getchannels'])
        def get_all_channels(message):
            try:
                if self.check_admin(message.chat.id):
                    channels = self._db.get("channels")
                    text = "لیست چنل ها:\n"
                    for i in channels["channels"]:
                        for key, value in i.items():
                            text = text + key + f" : تعداد کلیک شده {value}" + "\n"
                    self._bot.send_message(message.chat.id, text)
                else:
                    self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_messge(admins["main-admin"], f"{str(e)}")


        @self._bot.message_handler(func=lambda message: message.text.startswith("/delchannel"))
        def delet_channel(message):
            try:
                if self.check_admin(message.chat.id):
                    channel = message.text.split(" ")[1]

                    channels = self._db.get("channels")
                    if channel != None:
                        for i in channels["channels"]:
                            for key, value in i.items():
                                if channel == key:
                                    channels["channels"].remove(i)
                                else:
                                    continue
                        
                        self._db.update("channels", channels)
                        self._bot.send_message(message.chat.id, f"چنل {channel if channel[0] == '@' else '@' + channel} با موفقیت پاک شد.")
                    else:
                        self._bot.send_message(message.chat.id, "چنل پیدا نشد")
                else:
                    self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")


        @self._bot.message_handler(func=lambda message: message.text.startswith("/addchannel"))
        def add_channel(message):
            try:
                if self.check_admin(message.chat.id):
                    channel = message.text.split(' ')[1]

                    channels = self._db.get("channels")
                    if channel != None:
                        channels["channels"].append({channel: 0})
                        self._db.update("channels", channels)
                        self._bot.send_message(message.chat.id, f"چنل {channel if channel[1] == '@' else '@' + channel} با موفقیت اضافه شد.")
                    else:
                        self._bot.send_message(message.chat.id, "چنل پیدا شد")
                else:
                    self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")

        @self._bot.message_handler(func=lambda message: message.text.startswith("/addserv"))
        def addserver(message):
            try:
                if self.check_admin(message.chat.id):
                    host = message.text.split(' ')[1]
                    response = add_server(self._server, host, self._token)

                    if response == True:
                        self._bot.send_message(message.chat.id, "تمام شد. سرور با موفقیت اضافه شد.")
                    else:
                        self._bot.send_message(message.chat.id, f"اتفاثی افتاد لطفا دوباره تلاش کنید.\n{response}")
                else:
                    self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")
        
        
        @self._bot.message_handler(commands=["disk"])
        def disk_management(message):
            if self.check_admin(message.chat.id):
                try:
                    self._bot.send_message(message.chat.id, "در حال دریافت اطلاعات...")
                    data = get_disk_data(self._server, self._token)
                    if data:
                        try:
                            self._bot.send_message(message.chat.id,
                                    f"وضعیت:\nتمام حافظه: {data['totalspace']},\nحافظه آزاد: {data['freespace']}")
                        except:
                            main_admin = self._db.get("admins")
                            self._bot.send_message(main_admin["main-admin"], f"{data}")
                    else:
                        self._bot.send_message(message.chat.id, "مشکلی در دریافت اطالاعات پیش آمد")
                except Exception as e:
                    self._bot.send_message(message.chat.id, f"مشکلی در هنگام انجام عمل پیش آمد,\nجزئیات: {str(e)}")
            else:
                self._bot.send_message(message.chat.id, "لطفا به پنل ادمین وارد شوید", reply_markup=wellcome_murk("ورود به پنل ادمین", "login"))

        @self._bot.callback_query_handler(func=lambda call: True)
        def callect_data(call):
            try:
                admins = self._db.get('admins')

                if call.data == "login":
                    if self.check_admin(call.message.chat.id):
                        self._bot.send_message(call.message.chat.id, "خوش آمدید ادمین!", reply_markup=admin_panel([
                            {'text': 'disk manage', 'data': 'disk'},
                            {'text': 'add server', 'data': 'add-server'},
                            {'text': 'upload video', 'data': 'upload-video'},
                            {'text': 'manage channel', 'data': 'manage-channel'}
                        ], call.message.chat.id))
                    else:
                        self._bot.send_message(call.message.chat.id, "لطفا صبر کنید تا ادمین اصلی شمارا تایید کند")
                        self._bot.send_message(admins['main-admin'],
                            f"user {call.message.chat.id} requested for admin\nplease choose your choice",
                            reply_markup=allow_as_admin([
                            	{"text": "allow", "data": "allow-admin"},
                            	{"text": "dont allow", "data": "dontallow-admin"},
                            	str(call.message.chat.id)
                        ]))

                elif (call.data).split(" ")[0] == 'manage-channel':
                    self._bot.send_message(int((call.data).split(" ")[1]), "لطفا دستور /getchannels را وارد کنید تا لیست چنل هارا مشاهده کنید\nلطفا دستور /addchannel + @channelusername تا چنل اضافه شود\nلطفا دستور /delchannel + @channleusername تا چنل از لیست حذف شود")

                elif (call.data).split(" ")[0] == 'disk':
                    self._bot.send_message(int((call.data).split(" ")[1]), "لطفا دستور /disk را وارد کنید تا اطلاعات حافظه را دریافت کنید.")

                elif (call.data).split(" ")[0] == 'add-server':
                    self._bot.send_message(int((call.data).split(" ")[1]), "لطفا دستور /addserv + server name را ارسال کنید تا سرور اضافه شود، مثال:\n/addserv http://127.0.0.1")

                elif (call.data).split(" ")[0] == 'upload-video':
                    self._bot.send_message(int((call.data).split(" ")[1]), "لطفا دستور /uploadvideo را ارسال کنید تا پروسه شروع شود")

                elif (call.data).split(" ")[0] == "allow-admin":
                    admins['admins'].append(int((call.data).split(" ")[1]))
                    self._db.update("admins", admins)
                    self._bot.send_message(int((call.data).split(" ")[1]), "شما ادمین جدید هستید!\nحال میتوانید ربات را مدیریت کنید.", reply_markup=admin_panel([
                            {'text': 'disk manage', 'data': 'disk'},
                            {'text': 'add server', 'data': 'add-server'},
                            {'text': 'upload video', 'data': 'upload-video'},
                            {'text': 'manage channel', 'data': 'manage-channel'}
                        ], int((call.data).split(" ")[1])))

                elif (call.data).split(" ")[0] == "dontallow-admin":
                    self._bot.send_message(int((call.data).split(" ")[1]), "ادمین اصلی شمارا تایید نکرد.")

                elif (call.data).split(" ")[0] == "check-user-joined":
                    user_stat = self.check_member(call.message.chat.id)
                    channels = self._db.get("channels")
                    if user_stat == True:

                        self._bot.delete_message(call.message.chat.id, self._message_id)
                        j = 0
                        for i in channels["channels"]:
                            for key, value in i.items():
                                channels["channels"][j][key] += 1
                            j += 1
                        self.send_video_to_user(call.message.chat.id, (call.data).split(" ")[1])
                    else:
                        send = self._bot.send_message(call.message.chat.id,
                            "لطفا در چنل های زیر عضو شوید تا ویدئو ارسال شود",
                            reply_markup=join_channels(channels["channels"], (call.data).split(" ")[1]))
                        self._message_id = send.id
            except Exception as e:
                admins = self._db.get("admins")
                self._bot.send_message(admins["main-admin"], f"{str(e)}")


    def check_admin(self, user_id: int):
        try:
            data = self._db.get("admins")
            if user_id in data["admins"] or user_id == data["main-admin"]:
                return True
            else:
                return False
        except Exception as e:
            admins = self._db.get("admins")
            self._bot.send_message(admins["main-admin"], f"{str(e)}")


    def send_video_to_user(self, user_id, param):
        try:
            video = get_video(param, self._server, self._token)
            if str(type(video))[8:-2] == "bytes":
                vid_message = self._bot.send_video(user_id, video)
                self._bot.send_message(user_id, "لطفا ویدئو را به پیام های ذخیره شده خود فوروارد کنید.\nویدئو در 15 ثانیه دیگر پاک خواهد شد.")
                sleep(15)
                self._bot.delete_message(user_id, vid_message.id)
        except Exception as e:
            admins = self._db.get("admins")
            self._bot.send_message(admins["main-admin"], f"{str(e)}")


    def check_member(self, user_id):
        try:
            user_stat = self.get_member_stat(user_id)
            channels = self._db.get("channels")
            user = []
            for i in channels["channels"]:
                for key, value in i.items():
                    if user_stat[key] == "member":
                        user.append("member")
                    else:
                        user.append("not-member")
            return all(member == "member" for member in user)
        except Exception as e:
            admins = self._db.get("admins")
            self._bot.send_message(admins["main-admin"], f"{str(e)}")


    def get_member_stat(self, user_id):
        try:
            channels = self._db.get("channels")
            status = {}
            for i in channels["channels"]:
                for key, value in i.items():
                    chat_member = self._bot.get_chat_member('@' + key, user_id).status
                    status[key] = chat_member
            return status
        except Exception as e:
            admins = self._db.get("admins")
            self._bot.send_message(admins["main-admin"], f"{str(e)}")
            return False

    def run(self):
        try:
            self._bot.polling(none_stop=True, timeout=1000)
        except Exception as e:
            admins = self._db.get("admins")
            self._bot.send_message(admins["main-admin"], f"{str(e)}")



mybot = Bot("bot token")
mybot.run()

