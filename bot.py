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
import yadisk
from translate import Translator
# from telebot.types import ReplyKeyboardRemove, CallbackQuery

yandex_disk = yadisk.YaDisk(token=configs.yandex_disk_token)
ya_check_token=yandex_disk.check_token()
ya_video_dir="/ROOP/video_clips/films/watermark"
if not ya_check_token:
    print('Нужно обновить токен для доступа к яндексу')
    # bot.send_message(configs.logs_chat, f'{configs.stage} {err_text}')
    sys.exit(1)

translator= Translator(to_lang="Russian")

utc_tz = pytz.timezone('UTC')
bot = telebot.TeleBot(configs.bot_token,parse_mode='MARKDOWN')
 
userInfo = {}

def write_video_data():
    watermark_files=yandex_disk.listdir(ya_video_dir)
    # print(watermark_files)
    for item in watermark_files:
        found_ya_clip_in_db = False
        url = item['file']
        name_en=item['name'].split('.mp4')[0]
        get_video_clips_name=mysqlfunc.get_video_clips_name()
        for db_video_clips in get_video_clips_name:
            if name_en == db_video_clips['name_en']:
                # print(name_en +"=="+ db_video_clips['name_en'])
                found_ya_clip_in_db = True
                if db_video_clips['name_ru'] == '' or db_video_clips['name_ru'] == None or \
                   db_video_clips['path'] == None or db_video_clips['md5'] == None or \
                   db_video_clips['url'] == None:
                        # print("False1" + name_en)
                        found_ya_clip_in_db= False

        if not found_ya_clip_in_db:
            try:
                # name_ru = translator.translate(name_en)
                name_ru = name_en
                
            except:
                name_ru = name_en
            print(name_ru)
            mysqlfunc.set_video_clips(name_en,name_ru,item['file'],item['path'],item['md5'])
    #Удаляем из бд записи если файлов уже нет в яндексе
    path=True
    get_video_clips_name=mysqlfunc.get_video_clips_name(path)
    for db_video_clip_path in get_video_clips_name:
        if not (yandex_disk.exists(db_video_clip_path['path'])):
            mysqlfunc.del_video_clips_name(db_video_clip_path['path'])

def fillUserInfo(userInfo,message):
    current_time_utc = pytz.datetime.datetime.now(utc_tz)
    userInfo[str(message.chat.id)+'_record_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
    userInfo[str(message.chat.id)+'_botState'] = False
    userInfo[str(message.chat.id)+'_photoMessage'] = ''
    userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
    #если не существует возвращает None в бд запишется NUll message.from_user.first_name
    userInfo[str(message.chat.id)+'_First_name'] = message.from_user.first_name
    userInfo[str(message.chat.id)+'_Last_Name'] = message.from_user.last_name    
    return userInfo

@bot.message_handler(content_types=['text'])
def start(message):
    global userInfo

    if str(message.chat.id)+'_record_date' not in userInfo:
        userInfo=fillUserInfo(userInfo,message)
        # current_time_utc = pytz.datetime.datetime.now(utc_tz)
        # userInfo[str(message.chat.id)+'_record_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
        # userInfo[str(message.chat.id)+'_botState'] = False
        # userInfo[str(message.chat.id)+'_photoMessage'] = ''
        # userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
        # #если не существует возвращает None в бд запишется NUll message.from_user.first_name
        # userInfo[str(message.chat.id)+'_First_name'] = message.from_user.first_name
        # userInfo[str(message.chat.id)+'_Last_Name'] = message.from_user.last_name
    # elif userInfo[str(message.chat.id)+'_step'] == 'wait_video' and 'Спасибо, что выбираете наш сервис!' in message.text:
    #      userInfo=fillUserInfo(userInfo,message)
    # ############## debug
    print(message.chat.id)
    print(userInfo[str(message.chat.id)+'_record_date'])
    print(mysqlfunc.get_status(message.chat.id,userInfo[str(message.chat.id)+'_record_date'] ))
    try:
        if message.text == '/start' and not userInfo[str(message.chat.id)+'_botState'] \
            or mysqlfunc.get_status == 'complete':
            bot.send_message(message.from_user.id, 'Я рендринг бот 🤖 от компании GNEURO.\nА еще у нас есть [обучающий бот](https://t.me/gneuro_bot)')
            #Обновляем данные о клипах
            write_video_data()
            userInfo[str(message.chat.id)+'_botState']=True
            keyboard = types.InlineKeyboardMarkup()
            get_video_clips_name=mysqlfunc.get_video_clips_name()
            for clip in get_video_clips_name :
                    keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
            bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
        elif message.text == '/start' and userInfo[str(message.chat.id)+'_botState']=='wait_video':
            # bot.send_message(message.from_user.id, 'Бот уже запущен')
            userInfo[str(message.chat.id)+'_botState']=False
            bot.clear_step_handler_by_chat_id(message.from_user.id)
            start(message)
        elif message.text == '/stop':
            userInfo[str(message.chat.id)+'_botState']=False
            bot.clear_step_handler_by_chat_id(message.from_user.id)
            bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота')
            if (botStop(message)): return
    except Exception as err:
        text=f'{configs.stage} : Ошибка функция {message},user {message.from_user.id} err: {err}'
        print(err)
 
def photo(message):
    if (botStop(message)): return
    # userInfo[str(message.chat.id)+'_notice']=message.text;
    keyboard = types.ReplyKeyboardRemove()
    userInfo[str(message.chat.id)+'_photoList'] = []
    # userInfo[str(message.chat.id)+'_step'] = 'get_photo'
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_photo_stop = types.KeyboardButton(text='stop')
    keyboard.add(button_photo_stop)
    # bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=keyboard)
    # bot.register_next_step_handler(message, photo_handler);

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, 'Вы прислали видео вместо фотографии, эта функция пока не поддерживается')

@bot.message_handler(content_types=['document'])
def document_handler(message):
    if message.document.mime_type == 'video/mp4':
        bot.send_message(message.chat.id, 'Вы прислали видео вместо фотографии, эта функция пока не поддерживается')

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    print("photo handler function")
    # print("photo_step: " + userInfo[str(message.chat.id)+'_step'])
    if (message.content_type == 'text' and botStop(message)): return
    elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text':
        # bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографии')
        photo(message)
        # bot.register_next_step_handler(message, photo_handler);
    else:
        message.text='start'
        start(message)
    userInfo[str(message.chat.id)+'_photo'] = (message.photo[-1].file_id)
    save_result(message)

def save_result(message):
    global userInfo
    # print ("save to db")
    tg_user_id=message.from_user.id
    try:
        mysqlfunc.insert_user_data(userInfo[str(message.chat.id)+'_First_name'],userInfo[str(message.chat.id)+'_Last_Name'] \
            ,tg_user_id,userInfo[str(message.chat.id)+'_choose'],userInfo[str(message.chat.id)+'_record_date'])
    except Exception as err:
         print("Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}")
    #create local path store photo and text
    letters = string.ascii_lowercase
    rnd_string = ''.join(random.choice(letters) for i in range(4))
    file_info = bot.get_file(userInfo[str(message.chat.id)+'_photo'])
    downloaded_photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, 'Ваши данные приняты ролик формируется от 5 минут, в зависимости от нагрузки на сервис')
    userInfo[str(message.chat.id)+'_step'] = 'wait_video'

    try:
        mysqlfunc.insert_photos(downloaded_photo, tg_user_id, userInfo[str(message.chat.id)+'_record_date'])
        mysqlfunc.set_status(tg_user_id,'ready_to_render')
    except Exception as err:
        print(f'{configs.stage} : Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}')

                   
def botStop(message):
    if message.content_type == 'text':
        if (message.text.lower() == '/stop'):
            userInfo[str(message.chat.id)+'_botState']=False
            bot.send_message(message.chat.id, 'Бот остановлен,данные не сохранены, для перезапуска бота /start')
            return True 
 
@bot.callback_query_handler(func=lambda call: call.data)
def callback_worker(call):
        userInfo[str(call.message.chat.id)+'_choose'] = call.data
        bot.send_message(call.message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=types.ReplyKeyboardRemove())
        userInfo[str(call.message.chat.id)+'_step'] = 'get_photo'
        # bot.register_next_step_handler(call.message, photo);

if __name__=='__main__':
    # while True:
        try:
            # //check mysql connect
            mysqlfunc.get_task_to_render()
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            # bot.send_message(, f'{configs.stage} {e} --------- {trace}')
            print(f'{configs.stage} {e} --------- {trace}')