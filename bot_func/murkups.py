from telebot import types

def wellcome_murk(text: str, data: str):
    b1 = types.InlineKeyboardButton(text=text, callback_data=data)
    murk = types.InlineKeyboardMarkup()
    murk.add(b1)
    return murk

def allow_as_admin(data: list):
    b1 = types.InlineKeyboardButton(text=data[0]['text'], callback_data=data[0]['data'] + " " + data[2])
    b2 = types.InlineKeyboardButton(text=data[1]['text'], callback_data=data[1]['data'] + " " + data[2])

    mark = types.InlineKeyboardMarkup()
    mark.add(b1, b2)
    return mark

def admin_panel(data: list, id: int):
    murk = types.InlineKeyboardMarkup()
    for i in data:
        murk.add(types.InlineKeyboardButton(text=i['text'], callback_data=i['data'] + " " + str(id)))

    return murk

def join_channels(channels: list, param: str):
    murk = types.InlineKeyboardMarkup()
    for i in channels:
        for key, value in i.items():
            murk.add(types.InlineKeyboardButton(text="عضو شدن در چنل", url=f"https://t.me/{key}"))

    murk.add(types.InlineKeyboardButton(text="من عضو شدم", callback_data="check-user-joined " + param))
    return murk