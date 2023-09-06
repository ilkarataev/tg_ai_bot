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
# from yoomoney import Client
# from yoomoney import Quickpay

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

@bot.message_handler(commands=['contacts'])
def contacts(message):
    text = """ 
        Наши контакты:
        📌[Инстаграм](https://instagram.com/gneuroacademy?igshid=MzRlODBiNWFlZA==)
        🔴[YouTube](https://youtube.com/@GNeuro)
         ✔️[Telegram](https://t.me/GNeuro)
        🟢[WhatsApp](https://wa.me/79936225631?text=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82!%20%F0%9F%91%8B%20%D1%8F%20%D0%BF%D0%BE%20%D0%BF%D0%BE%D0%B2%D0%BE%D0%B4%D1%83%20%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F)
        """
    bot.send_message(message.from_user.id, text,disable_web_page_preview=True)

@bot.message_handler(commands=['stop'])
def stop(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
    bot.clear_step_handler_by_chat_id(message.from_user.id)
    userInfo.clear()
    bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота',reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    initialize_user_info(message)
    send_welcome_message(message)
    send_option_buttons(message)

@bot.message_handler(func=lambda message: message.text == 'Перезапуск бота')
def start(message):
    initialize_user_info(message)
    send_welcome_message(message)
    send_option_buttons(message)

@bot.message_handler(func=lambda message: message.text == 'Получить новую ссылку на оплату')
def payNewLink(message):
    pay(message)

# @bot.message_handler(func=lambda message: message.text == 'Хочу видео без вотермарки')
# def pay(message):
#     if message.text == '/stop': stop(message); return
#     bot.send_message(message.from_user.id, f'Для получения видео без вотермарки необходимо оплатить {configs.ym_service_price} рублей')
#     initialize_user_info(message)
#     userInfo[str(message.chat.id)+'_payCode'] = str(message.chat.id) + str(round(time.time() * 1000))
#     quickpay = Quickpay(
#             receiver=configs.ym_receiver,
#             quickpay_form="shop",
#             targets="pay for Video",
#             paymentType="SB",
#             sum=str(configs.ym_service_price),
#             label=userInfo[str(message.chat.id)+'_payCode']
#             )
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     keyboard.add(types.KeyboardButton(text='Оплатил'))
#     keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
#     keyboard.add(types.KeyboardButton(text='Получить новую ссылку на оплату'))
#     bot.send_message(message.chat.id, '<a href="'+quickpay.base_url+'">Оплатить</a>' \
#         +'\nПосле оплаты нажмите "Оплатил"', parse_mode="HTML",reply_markup=keyboard)
 
#     bot.register_next_step_handler(message, checkPay)

# @bot.message_handler(func=lambda message: message.text == 'Оплатил')
# def checkPay(message):
#     try:
#         tg_user_id=message.from_user.id
#         userInfo[str(message.chat.id)+'_payCode']=1668898671693986833691
#         if (str(message.chat.id)+'_payCode' not in userInfo):
#             pay(message)
#         print(str(userInfo[str(message.chat.id)+'_payCode']))
#         if message.text == '/stop': stop(message); return
#         if (message.text.lower() == 'оплатил'):
#             print('aaaa')
#             history = Client(configs.ym_wallet_token).operation_history(label=int((userInfo[str(message.chat.id)+'_payCode'])))
#             print(str(history))
#             for operation in history.operations:
#                 print(operation.status.lower())
#                 if (operation.status.lower() == 'success'):
#                     mysqlfunc.set_payment(tg_user_id, userInfo[str(message.chat.id)+'_record_date'])
#                     bot.send_message(message.chat.id,'Теперь вы можете сделать одно видео без вотермарки',reply_markup=types.ReplyKeyboardRemove())
#                     start(message)
#                     return
#             keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#             keyboard.add(types.KeyboardButton(text='Оплатил'))
#             keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
#             keyboard.add(types.KeyboardButton(text='Получить новую ссылку на оплату'))
#             bot.send_message(message.chat.id, 'Оплата еще не прошла. Попробуйте проверить позднее', reply_markup=keyboard);
#             bot.register_next_step_handler(message, checkPay)
#         else:
#             keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#             keyboard.add(yesBtn = types.KeyboardButton(text='Оплатил'))
#             keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
#             keyboard.add(types.KeyboardButton(text='Получить новую ссылку на оплату'))
#             bot.send_message(message.chat.id, 'Неизвестная команда.', reply_markup=keyboard);
#             bot.register_next_step_handler(message, checkPay)
#     except Exception as e:
#         print(f'Ошибка в функции оплаты {e}')
#         traceback.print_exc()
#         bot.send_message(message.chat.id, f'Произошла ошибка в оплате.Напишите нам на почту {email}');

@bot.message_handler(content_types=['text'])
def start(message):
    if str(message.chat.id)+'_record_date' not in userInfo:
            initialize_user_info(message)
    try:
        if message.text == '/start' and not userInfo[str(message.chat.id)+'_botState']:
            initialize_user_info(message)
            send_welcome_message(message)
            send_option_buttons(message)
        elif message.text == '/start' and userInfo[str(message.chat.id)+'_botState']:
            bot.send_message(message.from_user.id, 'Бот уже запущен')
        elif message.text == '/stop':
            stop(message)
        elif userInfo[str(message.chat.id)+'_step'] == 'wait_video' and 'Спасибо, что выбираете наш сервис!' in message.text:
            print("Видео получено") # debug
            remove_watermark_button = types.KeyboardButton("Хочу без ватермарка")
            keyboard.add(remove_watermark_button)
            bot.send_message(message.from_user.id, 'Хотите без ватермарка?', reply_markup=keyboard)
            userInfo[str(message.chat.id) + '_step'] = 'remove_watermark_option'
            bot.register_next_step_handler(message, handle_remove_watermark_option)
        elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text':
            bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
    except Exception as err:
        text = f'{configs.stage} : Ошибка функция {message}, user {message.from_user.id} err: {err}'
        print(err)

def initialize_user_info(message):
    current_time_utc = pytz.datetime.datetime.now(utc_tz)
    userInfo[str(message.chat.id)+'_record_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
    userInfo[str(message.chat.id)+'_botState'] = False
    userInfo[str(message.chat.id)+'_photoMessage'] = ''
    userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
    userInfo[str(message.chat.id)+'_First_name'] = message.from_user.first_name
    userInfo[str(message.chat.id)+'_Last_Name'] = message.from_user.last_name
    userInfo[str(message.chat.id)+'_category'] = ''

def send_welcome_message(message):
    bot.send_message(message.from_user.id, ' \
    Я рендринг бот 🤖 от компании GNEURO.\n \
    🧠🚀 Мы обучаем работе с нейросетями.\n \
    Вы можете посетить наш сайт: [Gneuro.ru/sd](https://gneuro.ru/sd)')
    userInfo[str(message.chat.id)+'_botState'] = True

def send_video_clip_categories(message):
    if message.text == '/stop': stop(message); return

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_category = mysqlfunc.get_video_clips_name('category')
    for category in get_video_clips_category:
        keyboard.add(types.KeyboardButton(text=category['category']))
    bot.send_message(message.from_user.id, 'Выберите категорию видео', reply_markup=keyboard)
    userInfo[str(message.chat.id)+'_step'] = 'get_category'
    bot.register_next_step_handler(message, choose_clip_name)

def choose_clip_name(message):
    if message.text == '/stop': stop(message); return
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',message.text)
    for clip in get_video_clips_name :
            # keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
            keyboard.add(types.KeyboardButton(text=clip['name_en']))    
    bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
    userInfo[str(message.chat.id)+'_step'] = 'get_clip_name'
    bot.register_next_step_handler(message, photo_handler);

def send_option_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Стать героем видео"), \
        types.KeyboardButton("Хочу сам делать дипфейки в нейросетях", web_app=types.WebAppInfo("https://gneuro.ru/sd")))
    bot.send_message(message.from_user.id, 'Выберите одну из опций:', reply_markup=keyboard)
    userInfo[str(message.chat.id) + '_step'] = 'get_option'
    bot.register_next_step_handler(message, handle_option)

def handle_option(message):
    if message.text == '/stop': stop(message); return
    if message.text == "Стать героем видео":
        send_video_clip_categories(message)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, выберите одну из опций.')

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, 'Функция обработки видео пока не доступна',reply_markup=types.ReplyKeyboardRemove())
    if userInfo[str(message.chat.id)+'_step'] == 'get_photo':
        bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
        return

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    if message.text == '/stop': stop(message); return
    if (message.content_type == 'text') and userInfo[str(message.chat.id)+'_step'] == 'get_clip_name':
        userInfo[str(message.chat.id)+'_choose'] = message.text
        userInfo[str(message.chat.id)+'_step'] = 'get_photo'
        bot.send_photo(chat_id=message.chat.id, photo=open('./libs/imgs/photo_example.jpg', 'rb'),caption='Пример как правильно делать фото')
        bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографию',reply_markup=types.ReplyKeyboardRemove())
        
        return
    elif  message.content_type == 'photo' and str(message.chat.id)+'_botState' not in userInfo:
        bot.send_message(message.chat.id, 'Ошибка фотография отправленно до запуска бота.Нажмите /start')
    elif (message.content_type == 'photo' and userInfo[str(message.chat.id)+'_step'] == 'get_photo'):
        userInfo[str(message.chat.id)+'_photo'] = (message.photo[-1].file_id)
        save_result(message)
    # elif (message.content_type == 'text' and botStop(message)): return
    else: #проверить как это работает и надо ли нам оно
        message.text='start'
        start(message)

def save_result(message):
    userInfo[str(message.chat.id)+'_record_date'] = pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S')
    tg_user_id=message.from_user.id
    try:
        mysqlfunc.insert_user_data(userInfo[str(message.chat.id)+'_First_name'],userInfo[str(message.chat.id)+'_Last_Name'] \
            ,tg_user_id,userInfo[str(message.chat.id)+'_choose'],userInfo[str(message.chat.id)+'_record_date'])
    except Exception as err:
         print(f"Ошибка на стадии сохранения фото err: {err}")
    letters = string.ascii_lowercase
    rnd_string = ''.join(random.choice(letters) for i in range(4))
    file_info = bot.get_file(userInfo[str(message.chat.id)+'_photo'])
    downloaded_photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, 'Ваши данные приняты.\n \
        Видео формируется от 5 минут, в зависимости от нагрузки на сервис')
    userInfo[str(message.chat.id)+'_step'] = 'wait_video'

    try:
        mysqlfunc.insert_photos(downloaded_photo, tg_user_id, userInfo[str(message.chat.id)+'_record_date'])
        mysqlfunc.set_status(tg_user_id,'ready_to_render',userInfo[str(message.chat.id)+'_record_date'])
    except Exception as err:
        print(f'{configs.stage} : Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}')

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