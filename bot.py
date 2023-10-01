# import re,os.path,shutil,yadisk
import traceback,sys,pytz
import string,random,re,time
import random
import telebot 
from telebot import types
from libs import config as configs
from libs import mysql as mysqlfunc
from datetime import datetime
import logging
from telebot.types import ReplyKeyboardRemove, CallbackQuery

utc_tz = pytz.timezone('UTC')
bot = telebot.TeleBot(configs.bot_token,parse_mode='MARKDOWN')
email='Agency@gneuro.ru' 
userInfo = {}

@bot.message_handler(commands=['about'])
def about(message):
    text = """
        Тут мы расскажем немного о боте! ❤️

        Это Бот🤖 академии Gneuro [Gneuro.ru](https://gneuro.ru/)
        Твой проводник в мир нейросетей.⚡️🧠🚀 
        1. Выбери тему для видео.
        2. Загрузи фото.
        3. Подождать пока трудится нейросеть.
        4. Бот отправит видеo в тот же чат.
        5. Улыбнуться при просмотре видео.

        Есть  вопросы по нейросетям❓
        Напиши нам и мы расскажем @gneuroacademy
        Остальное смотри на сайте [Gneuro.ru](https://gneuro.ru/)
        """
    bot.send_message(message.from_user.id, text)
    return

@bot.message_handler(commands=['contacts'])
def contacts(message):
    text = """ 
        Наши контакты:
        📌[Инстаграм](https://instagram.com/gneuroacademy?igshid=MzRlODBiNWFlZA==)
        🔴[YouTube](https://youtube.com/@GNeuro)
         ✔️[Telegram](https://t.me/GNeuro)
        🟢[WhatsApp](https://wa.me/79936225631?text=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82!%20%F0%9F%91%8B%20%D1%8F%20%D0%BF%D0%BE%20%D0%BF%D0%BE%D0%B2%D0%BE%D0%B4%D1%83%20%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F)
        """
    bot.send_message(message.from_user.id, text, disable_web_page_preview=True)
    return


@bot.message_handler(commands=['donate'])
def donate(message):
    bot.send_photo(chat_id=message.chat.id, photo=open('./libs/imgs/qr.png', 'rb'),caption='СБП донат')
    text = """ 
        Нашему проекту нужен небольшой донат для развития.
        Если вы получили позитивные эмоции и улыбнулись.
        По QR коду можно поддержать наш проект.
        Мы уже отрендрили свыше тысячи роликов бесплатно.
        И у нас еще тысячи идей для новых роликов.
        Закинь больше всех и получишь + к карме.
        """
    bot.send_message(message.from_user.id, text, disable_web_page_preview=True)
    return

@bot.message_handler(commands=['stop'])
def stop(message):
    print( mysqlfunc.check_user_render_queue(message.from_user.id))
    if not mysqlfunc.check_user_render_queue(message.from_user.id):
        bot.send_message(message.chat.id, 'Видео в очереди на обработку, пожайлуста ожидайте готового видео',reply_markup=types.ReplyKeyboardRemove())
        return
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
    bot.clear_step_handler_by_chat_id(message.from_user.id)
    userInfo.clear()
    mysqlfunc.clean_unfinish(message.from_user.id)
    bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота',reply_markup=keyboard)

def initialize_user_info(message):
    userInfo[str(message.chat.id)+'_category'] = ''
    userInfo[str(message.chat.id)+'_get_video_clips_names'] =''
    userInfo[str(message.chat.id)+'_photo'] = ''

def send_welcome_message(message):
    bot.send_message(message.from_user.id, ' \
    Я рендринг бот 🤖 от компании GNEURO.\n \
    🧠🚀 Мы обучаем работе с нейросетями.\n \
    Вы можете посетить наш сайт: [Gneuro.ru/sd](https://gneuro.ru/sd)')
    bot.send_message(message.from_user.id, "Если вы не видите клавиатуру, нажмите на иконку с четырьмя квадратами внизу экрана, чтобы ее развернуть.")
def first_step_render(message):
    print('first_step_render ' +str(mysqlfunc.get_bot_step(message.chat.id)))
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    if message.text == '/donate': donate(message)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Стать героем видео 🦸"), \
        types.KeyboardButton("Хочу сам делать дипфейки в нейросетях 🧠💻🔧", web_app=types.WebAppInfo("https://gneuro.ru/sd")), \
        types.KeyboardButton("Поддержать проект 🍩💸🍩"))
    bot.send_message(message.from_user.id, 'Выберите одну из опций:', reply_markup=keyboard)
    mysqlfunc.insert_bot_step(message.chat.id,'first_step_render',pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
    bot.register_next_step_handler(message, handle_option)

def handle_option(message):
    print('handle_option ' +str(mysqlfunc.get_bot_step(message.chat.id)))
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    if message.text == '/donate': donate(message)
    if message.text == "Стать героем видео" or mysqlfunc.get_bot_step(message.chat.id) == 'back_to_category':
        mysqlfunc.insert_bot_step(message.chat.id, 'go_to_category', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        video_clip_categories(message)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Стать героем видео"), \
            types.KeyboardButton("Хочу сам делать дипфейки в нейросетях", web_app=types.WebAppInfo("https://gneuro.ru/sd")))
        bot.send_message(message.from_user.id, 'Пожалуйста, выберите одну из опций.',reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_option)

def video_clip_categories(message):
    db_step=mysqlfunc.get_bot_step(message.chat.id)
    print('video_clip_categories ' +str(db_step))
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    if message.text == '/donate': donate(message)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_category = mysqlfunc.get_video_clips_name('category')
    categories = [item['category'] for item in get_video_clips_category]
    for category in get_video_clips_category:
        keyboard.add(types.KeyboardButton(text=category['category']))
    if db_step == 'go_to_category' and message.text == 'Стать героем видео' or \
        db_step == 'go_to_category' and message.text == 'Вернуться к выбору каталога':
        bot.send_message(message.from_user.id, 'Выберите категорию видео', reply_markup=keyboard)
        mysqlfunc.insert_bot_step(message.chat.id,'get_category',pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        bot.register_next_step_handler(message, choose_clip_name)
    elif db_step == 'go_to_category' and message.text in categories:
        mysqlfunc.insert_bot_step(message.chat.id,'get_category',pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        choose_clip_name(message)
    else:

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
        bot.send_message(message.from_user.id, 'Выберите категорию видео',reply_markup=keyboard)
        bot.register_next_step_handler(message, video_clip_categories)

def choose_clip_name(message):
    print("choose_clip_name")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_category = mysqlfunc.get_video_clips_name('category')
    categories = [item['category'] for item in get_video_clips_category]
    if  message.text in categories:
        userInfo[str(message.chat.id)+'_category'] = message.text
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    if message.text == '/donate': donate(message)

    if mysqlfunc.get_bot_step(message.chat.id) == 'get_category' and userInfo[str(message.chat.id)+'_category'] in categories:
        get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',message.text)
        for clip in get_video_clips_name :
                keyboard.add(types.KeyboardButton(text=clip['name_en']))
        keyboard.add(types.KeyboardButton(text='Вернуться к выбору каталога'))
        bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
        mysqlfunc.insert_bot_step(message.chat.id, 'get_clip_name', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        bot.register_next_step_handler(message, photo_handler)  
    else:
        get_video_clips_category = mysqlfunc.get_video_clips_name('category')
        for category in get_video_clips_category:
            keyboard.add(types.KeyboardButton(text=category['category']))
        bot.send_message(message.from_user.id, 'Выберите категорию видео',reply_markup=keyboard)
        bot.register_next_step_handler(message, choose_clip_name)


@bot.message_handler(commands=['start'])
def start(message):
    if not mysqlfunc.check_user_render_queue(message.from_user.id):
        bot.send_message(message.chat.id, 'Видео в очереди на обработку, пожайлуста ожидайте готового видео')
        return
    mysqlfunc.insert_tg_users(message.from_user.first_name, \
                              message.from_user.last_name, \
                              message.from_user.id, \
                              message.from_user.username, \
                              message.from_user.language_code, \
                              pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
    mysqlfunc.insert_bot_step(message.chat.id, '', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
    initialize_user_info(message)
    send_welcome_message(message)
    first_step_render(message)


@bot.message_handler(func=lambda message: message.text == 'Перезапуск бота')
def restart(message):
    start(message)

@bot.message_handler(func=lambda message: message.text == 'Помочь проекту')
def donate_button(message):
    donate(message)

@bot.message_handler(func=lambda message: message.text == 'Вернуться к выбору каталога')
def back(message):
    mysqlfunc.insert_bot_step(message.chat.id, 'back_to_category', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
    handle_option(message)

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, 'Функция обработки видео пока не доступна',reply_markup=types.ReplyKeyboardRemove())
    if not mysqlfunc.check_user_render_queue(message.from_user.id):
        bot.send_message(message.chat.id, 'Видео в очереди на обработку, пожайлуста ожидайте готового видео')
        return
    if mysqlfunc.get_bot_step(message.chat.id) == 'get_photo':
        bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
        return

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    print('photo_handler')
    step=mysqlfunc.get_bot_step(message.chat.id)
    if str(message.chat.id)+'_category' in userInfo:
        get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',userInfo[str(message.chat.id)+'_category'])
        get_video_clips_names = [item['name_en'] for item in get_video_clips_name]
        if  message.text in get_video_clips_names:
            userInfo[str(message.chat.id)+'_get_video_clips_names']=message.text
        if message.text == '/stop': stop(message); return
        if (message.text == 'Вернуться к выбору каталога'):back(message); return
        if message.text == '/about': about(message)
        if message.text == '/contacts': contacts(message)
        if message.text == '/donate': donate(message)
        if message.text == '/start': stop(message); return
        if (message.text == 'Использовать тоже фото'):
            bot.send_photo(chat_id=message.chat.id, photo=userInfo[str(message.chat.id)+'_photo'], caption='Будет использовано это фото')
            mysqlfunc.insert_bot_step(message.chat.id, 'get_previous_photo', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
            save_result(message)
        elif (message.content_type == 'photo' and step == 'get_photo'):
            userInfo[str(message.chat.id)+'_photo'] = (message.photo[-1].file_id)
            save_result(message)
        elif step == 'get_clip_name' and userInfo[str(message.chat.id)+'_get_video_clips_names'] in get_video_clips_names \
            or step == 'get_photo' and userInfo[str(message.chat.id)+'_get_video_clips_names'] in get_video_clips_names:
            userInfo[str(message.chat.id)+'_choose'] = message.text
            mysqlfunc.insert_user_data(message.from_user.first_name, message.from_user.last_name, message.chat.id, userInfo[str(message.chat.id)+'_choose'])
            mysqlfunc.insert_bot_step(message.chat.id, 'get_photo', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
            bot.send_photo(chat_id=message.chat.id, photo=open('./libs/imgs/photo_example.jpg', 'rb'),caption='Пример как правильно делать фото')
            get_previous_photo = mysqlfunc.get_photo_to_render(message.chat.id,'check')
            #Новый функционал предлагать последние фото
            if get_previous_photo:
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                keyboard.add(types.KeyboardButton("Использовать тоже фото"))
                userInfo[str(message.chat.id)+'_photo'] = get_previous_photo
                bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(message, photo_handler)
        elif  message.content_type == 'photo' and str(message.chat.id)+'_botState' not in userInfo:
            bot.send_message(message.chat.id, 'Ошибка фотография отправленно до запуска бота.Нажмите /start')
        else: #проверить как это работает и надо ли нам оно
            bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии')
            bot.register_next_step_handler(message, photo_handler)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
        keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
        bot.clear_step_handler_by_chat_id(message.from_user.id)
        userInfo.clear()
        bot.send_message(message.from_user.id, 'Возникла ошибка в боте',reply_markup=keyboard)
        bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота',reply_markup=keyboard)

def save_result(message):
    print('save_result')
    record_date = pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S')

    tg_user_id=message.from_user.id
    if userInfo[str(message.chat.id)+'_photo'] and mysqlfunc.get_bot_step(message.chat.id) == 'get_previous_photo':
        downloaded_photo = userInfo[str(message.chat.id)+'_photo']
    else:
        letters = string.ascii_lowercase
        # rnd_string = ''.join(random.choice(letters) for i in range(4))
        file_info = bot.get_file(userInfo[str(message.chat.id)+'_photo'])
        downloaded_photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, 'Ваши данные приняты.\n \
        Видео ' + str(userInfo[str(message.chat.id)+'_choose']) + ' формируется от 5 минут, в зависимости от нагрузки на сервис', \
        reply_markup=ReplyKeyboardRemove())
    mysqlfunc.insert_bot_step(message.chat.id, 'wait_video', pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

  # Проверяем, есть ли запись с такой же датой в таблице photos
    if mysqlfunc.check_record_exists(tg_user_id, record_date):  
        print(f"Запись уже существует для пользователя {tg_user_id} и даты {record_date}")
        return
    else:
        try:
            mysqlfunc.insert_photos(downloaded_photo, tg_user_id, record_date)
            try:
                mysqlfunc.update_user_data(downloaded_photo, tg_user_id, record_date)
                mysqlfunc.set_status(tg_user_id, 'ready_to_render', record_date)
            except Exception as err:
                print(f"Ошибка на стадии сохранения в таблицу users err: {err}")
        except Exception as err:
            print(f'{configs.stage} : Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}')

@bot.message_handler(content_types=['text'])
def return_state(message):
    step = mysqlfunc.get_bot_step(message.chat.id)
    print('message to function' + str(step))
    if step == 'first_step_render':
        first_step_render(message)
    elif step == 'back_to_category':
        handle_option(message)
    elif step == 'go_to_category':
        video_clip_categories(message)
    elif step == 'get_category':
        choose_clip_name(message)
    elif step == 'get_clip_name':
        photo_handler(message)
    elif step == 'get_photo':
        photo_handler(message)
    else:
        stop(message)

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