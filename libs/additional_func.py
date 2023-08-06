import re

def match_ru_text(text):
    if bool(re.search('[а-яА-Я]', text)) and not bool(re.search('[a-zA-Z]', text)):
        return  True
    else:
        return False

def getStringFromDB(string, format=''): #format не обязательный параметр!!
    formattedStr = string.replace(' \\n ', '\n') #переносы строки!
    if (format=='bold'):
        return '<b>' + formattedStr + '</b>'
    elif (format == 'strong'):
        return '<strong>' + formattedStr + '</strong>'
    elif (format == 'italic'):
        return '<i>' + formattedStr + '</i>'
    else:
        return formattedStr

def dev_auto_btn(bot, types, message,msgtext):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_live_area = types.KeyboardButton(text=msgtext)
    keyboard.add(button_live_area)
    bot.send_message(message.from_user.id, 'Тестовый ответ, нажми на кнопку',reply_markup=keyboard);


def yes_no_keyboardkeyboard(types):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    yesBtn = types.KeyboardButton(text='Да')
    noBtn = types.KeyboardButton(text='Нет')
    keyboard.add(yesBtn)
    keyboard.add(noBtn)
    return keyboard