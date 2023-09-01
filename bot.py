# import re,os.path,shutil,yadisk
import traceback,sys,pytz
import string,random,re,time
import random
import telebot 
from telebot import types
from libs import config as configs
from libs import mysql as mysqlfunc
from libs import yandex_libs as yalib
from datetime import datetime
import logging
from telebot.types import ReplyKeyboardRemove, CallbackQuery

utc_tz = pytz.timezone('UTC')
bot = telebot.TeleBot(configs.bot_token,parse_mode='MARKDOWN')
 
userInfo = {}

# def fillUserInfo(userInfo,message):
#     current_time_utc = pytz.datetime.datetime.now(utc_tz)
#     userInfo[str(message.chat.id)+'_record_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
#     userInfo[str(message.chat.id)+'_botState'] = False
#     userInfo[str(message.chat.id)+'_photoMessage'] = ''
#     userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
#     #если не существует возвращает None в бд запишется NUll message.from_user.first_name
#     userInfo[str(message.chat.id)+'_First_name'] = message.from_user.first_name
#     userInfo[str(message.chat.id)+'_Last_Name'] = message.from_user.last_name    
#     return userInfo

@bot.message_handler(content_types=['text'])
def start(message):
    if str(message.chat.id)+'_record_date' not in userInfo:
        # userInfo=fillUserInfo(userInfo,message)
        current_time_utc = pytz.datetime.datetime.now(utc_tz)
        userInfo[str(message.chat.id)+'_record_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
        userInfo[str(message.chat.id)+'_botState'] = False
        userInfo[str(message.chat.id)+'_photoMessage'] = ''
        userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
        #если не существует возвращает None в бд запишется NUll message.from_user.first_name
        userInfo[str(message.chat.id)+'_First_name'] = message.from_user.first_name
        userInfo[str(message.chat.id)+'_Last_Name'] = message.from_user.last_name
        userInfo[str(message.chat.id)+'_category'] =''
    try:
        if message.text == '/start' and not userInfo[str(message.chat.id)+'_botState']:
            bot.send_message(message.from_user.id, 'Я рендринг бот 🤖 от компании GNEURO.\nА еще у нас есть [обучающий бот](https://t.me/gneuro_bot)')
            #Обновляем данные о клипах
            userInfo[str(message.chat.id)+'_botState']=True
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
            # keyboard = types.InlineKeyboardMarkup()
            get_video_clips_category=mysqlfunc.get_video_clips_name('category')
            for category in get_video_clips_category :
                    # keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
                    keyboard.add(types.KeyboardButton(text=category['category']))
            # get_video_clips_name=mysqlfunc.get_video_clips_name()
            # for clip in get_video_clips_name :
                    # keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
                    # keyboard.add(types.KeyboardButton(text=clip['name_en']))
            bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
            userInfo[str(message.chat.id)+'_step'] = 'get_category'
            bot.register_next_step_handler(message, choose_clip_name);
        elif message.text == '/start' and userInfo[str(message.chat.id)+'_botState']:
            bot.send_message(message.from_user.id, 'Бот уже запущен')
        elif message.text == '/stop':
            userInfo[str(message.chat.id)+'_botState']=False
            bot.clear_step_handler_by_chat_id(message.from_user.id)
            bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота')
            if (botStop(message)): return
        elif userInfo[str(message.chat.id)+'_step'] == 'wait_video' and 'Спасибо, что выбираете наш сервис!' in message.text:
            print("Видео получено") #debug
        elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text':
            bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
            return
    except Exception as err:
        text=f'{configs.stage} : Ошибка функция {message},user {message.from_user.id} err: {err}'
        print(err)

def choose_clip_name(message):
    print(message.text)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',message.text)
    # print(get_video_clips_name)
    for clip in get_video_clips_name :
            print(clip['name_en'])
            # keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
            keyboard.add(types.KeyboardButton(text=clip['name_en']))
    bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
    userInfo[str(message.chat.id)+'_step'] = 'get_clip_name'
    bot.register_next_step_handler(message, photo_handler);

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, 'Функция обработки видео пока не доступна',reply_markup=types.ReplyKeyboardRemove())
    if userInfo[str(message.chat.id)+'_step'] == 'get_photo':
        bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
        return

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    if (message.content_type == 'text') and userInfo[str(message.chat.id)+'_step'] == 'get_clip_name':
        userInfo[str(message.chat.id)+'_choose'] = message.text
        userInfo[str(message.chat.id)+'_step'] = 'get_photo'
        bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=types.ReplyKeyboardRemove())
        return
    elif  message.content_type == 'photo' and str(message.chat.id)+'_botState' not in userInfo:
        bot.send_message(message.chat.id, 'Ошибка фотография отправленно до запуска бота.Нажмите /start')
    elif (message.content_type == 'photo' and userInfo[str(message.chat.id)+'_step'] == 'get_photo'):
        userInfo[str(message.chat.id)+'_photo'] = (message.photo[-1].file_id)
        save_result(message)
    elif (message.content_type == 'text' and botStop(message)): return
    else:
        message.text='start'
        start(message)

def save_result(message):
    userInfo[str(message.chat.id)+'_record_date'] = pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S')
    tg_user_id=message.from_user.id
    try:
        mysqlfunc.insert_user_data(userInfo[str(message.chat.id)+'_First_name'],userInfo[str(message.chat.id)+'_Last_Name'] \
            ,tg_user_id,userInfo[str(message.chat.id)+'_choose'],userInfo[str(message.chat.id)+'_record_date'])
    except Exception as err:
         print("Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}")
    letters = string.ascii_lowercase
    rnd_string = ''.join(random.choice(letters) for i in range(4))
    file_info = bot.get_file(userInfo[str(message.chat.id)+'_photo'])
    downloaded_photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, 'Ваши данные приняты ролик формируется от 5 минут, в зависимости от нагрузки на сервис')
    userInfo[str(message.chat.id)+'_step'] = 'wait_video'

    try:
        mysqlfunc.insert_photos(downloaded_photo, tg_user_id, userInfo[str(message.chat.id)+'_record_date'])
        mysqlfunc.set_status(tg_user_id,'ready_to_render',userInfo[str(message.chat.id)+'_record_date'])
    except Exception as err:
        print(f'{configs.stage} : Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}')

def botStop(message):
    if message.content_type == 'text':
        if (message.text.lower() == '/stop'):
            userInfo[str(message.chat.id)+'_botState']=False
            bot.send_message(message.chat.id, 'Бот остановлен,данные не сохранены, для перезапуска бота /start')
            return True 

if __name__=='__main__':
        try:
            # //check mysql connect
            mysqlfunc.get_task_to_render()
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            # bot.send_message(message.chat.id, 'Ошибка в работе бота',reply_markup=types.ReplyKeyboardRemove())
            # bot.send_message(, f'{configs.stage} {e} --------- {trace}')
            print(f'{configs.stage} {e} --------- {trace}')