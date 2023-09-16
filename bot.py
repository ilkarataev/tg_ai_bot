# import re,os.path,shutil,yadisk
import traceback,sys,pytz
import string,random,re,time, uuid
import random, telebot, logging,asyncio,json
from telebot import types
from libs import config as configs
from libs import mysql as mysqlfunc
from datetime import datetime
from telebot.types import ReplyKeyboardRemove, CallbackQuery, LabeledPrice,ShippingOption

utc_tz = pytz.timezone('UTC')
bot = telebot.TeleBot(configs.bot_token,parse_mode='MARKDOWN')
email='Agency@gneuro.ru' 
userInfo = {}

provider_token = configs.SHOP_API_TOKEN

@bot.message_handler(commands=['pay'])
def pay(message):
    prices = [
        LabeledPrice(label='10 видео рендеров в нашем боте', amount=5900), LabeledPrice('Коммисия', 500)
        # LabeledPrice(label='Подписка на месяц', amount=14900), LabeledPrice('Коммисия', 500)
        ]

    bot.send_invoice(
                     message.chat.id,  #chat_id
                     'Оплата рендеров для бота', #title
                     'Вы вызвали оплату для бота.\n Будет больше смешных видео  вашим лицом.', #description
                     'Bot render', #invoice_payload
                     provider_token, #provider_token
                     'rub', #currency
                     prices, #prices)
                     photo_url='https://static.tildacdn.com/tild3234-6632-4661-a130-616565623231/Nikitadot_Photograph.png',
                     photo_height=512,  # !=0/None or picture won't be shown
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False)  # True If you need to set up Shipping Fee
                    #  start_parameter='time-machine-example')

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Попытка оплаты была прервана из-за какой-то ошибки, попробуйте снова через несколько минут.")

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    summ=message.successful_payment.total_amount / 100
    current_time_utc = pytz.datetime.datetime.now(utc_tz)
    userInfo[str(message.chat.id)+'_pay_date'] = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
    bot.send_message(message.chat.id,
                     'Спасибо за платеж на сумму `{} {}` ! '.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')
    mysqlfunc.insert_payment(message.message.chat.id,'1',summ,userInfo[str(message.chat.id)+'_pay_date'])

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
@bot.message_handler(func=lambda message: message.text == 'Вернуться к выбору каталога')
def back(message):
    userInfo[str(message.chat.id) + '_step'] = 'back_to_category'
    handle_option(message)

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
        elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text' and message.text == 'Использовать тоже фото':
            bot.send_photo(chat_id=message.chat.id, photo=userInfo[str(message.chat.id)+'_photo'], caption='Будет использовано это фото',reply_markup=ReplyKeyboardRemove())
            userInfo[str(message.chat.id)+'_get_previous_photo'] = True
            save_result(message)
        elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text':
            bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
            keyboard.add(types.KeyboardButton(text='Перезапуск бота'))
            bot.clear_step_handler_by_chat_id(message.from_user.id)
            userInfo.clear()
            bot.send_message(message.from_user.id, 'Возникла ошибка в боте',reply_markup=keyboard)
            bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота',reply_markup=keyboard)
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
    userInfo[str(message.chat.id)+'_get_video_clips_names']=''
    userInfo[str(message.chat.id)+'_get_previous_photo'] = False
    userInfo[str(message.chat.id)+'_step'] =''
    userInfo[str(message.chat.id)+'_photo']=''

def send_welcome_message(message):
    bot.send_message(message.from_user.id, ' \
    Я рендринг бот 🤖 от компании GNEURO.\n \
    🧠🚀 Мы обучаем работе с нейросетями.\n \
    Вы можете посетить наш сайт: [Gneuro.ru/sd](https://gneuro.ru/sd)')
    userInfo[str(message.chat.id)+'_botState'] = True

def send_option_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Стать героем видео"), \
        types.KeyboardButton("Хочу сам делать дипфейки в нейросетях", web_app=types.WebAppInfo("https://gneuro.ru/sd")))
    bot.send_message(message.from_user.id, 'Выберите одну из опций:', reply_markup=keyboard)
    userInfo[str(message.chat.id) + '_step'] = 'get_option'
    bot.register_next_step_handler(message, handle_option)

def handle_option(message):
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    if message.text == "Стать героем видео" or userInfo[str(message.chat.id) + '_step'] == 'back_to_category':
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        userInfo[str(message.chat.id) + '_step'] = 'go_to_category'
        video_clip_categories(message)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, выберите одну из опций.')
        bot.register_next_step_handler(message, handle_option)

def video_clip_categories(message):
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
    get_video_clips_category = mysqlfunc.get_video_clips_name('category')
    categories = [item['category'] for item in get_video_clips_category]
    for category in get_video_clips_category:
        keyboard.add(types.KeyboardButton(text=category['category']))
    if userInfo[str(message.chat.id) + '_step'] == 'go_to_category' and message.text == 'Стать героем видео':
        bot.send_message(message.from_user.id, 'Выберите категорию видео', reply_markup=keyboard)
        userInfo[str(message.chat.id)+'_step'] = 'get_category'
        bot.register_next_step_handler(message, choose_clip_name)
    elif userInfo[str(message.chat.id) + '_step'] == 'go_to_category' and message.text in categories:
        userInfo[str(message.chat.id)+'_step'] = 'get_category'
        choose_clip_name(message)
    else:
        bot.send_message(message.from_user.id, 'Выберите категорию видео',reply_markup=keyboard)
        bot.register_next_step_handler(message, video_clip_categories)

def choose_clip_name(message):
    print("choose_clip_name")
    get_video_clips_category = mysqlfunc.get_video_clips_name('category')
    categories = [item['category'] for item in get_video_clips_category]
    if  message.text in categories:
        userInfo[str(message.chat.id)+'_category']=message.text
    if message.text == '/stop': stop(message); return
    if message.text == '/about': about(message)
    if message.text == '/contacts': contacts(message)

    if userInfo[str(message.chat.id)+'_step'] == 'get_category' and userInfo[str(message.chat.id)+'_category'] in categories:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False)
        get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',message.text)
        for clip in get_video_clips_name :
                # keyboard.add(types.InlineKeyboardButton(text=clip['name_ru'], callback_data=clip['name_en']))
                keyboard.add(types.KeyboardButton(text=clip['name_en']))
        keyboard.add(types.KeyboardButton(text='Вернуться к выбору каталога'))
        bot.send_message(message.from_user.id, 'Выберите тему видео для обработки вашей фотографии', reply_markup=keyboard)
        userInfo[str(message.chat.id)+'_step'] = 'get_clip_name'
        bot.register_next_step_handler(message, photo_handler)  
    else:
        get_video_clips_category = mysqlfunc.get_video_clips_name('category')
        for category in get_video_clips_category:
            keyboard.add(types.KeyboardButton(text=category['category']))
        bot.send_message(message.from_user.id, 'Выберите категорию видео',reply_markup=keyboard)
        bot.register_next_step_handler(message, choose_clip_name)

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, 'Функция обработки видео пока не доступна',reply_markup=types.ReplyKeyboardRemove())
    if userInfo[str(message.chat.id)+'_step'] == 'get_photo':
        bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографию')
        return

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    print('photo_handler')
    if str(message.chat.id)+'_category' in userInfo:
        get_video_clips_name=mysqlfunc.get_video_clips_name('by_category',userInfo[str(message.chat.id)+'_category'])
        get_video_clips_names = [item['name_en'] for item in get_video_clips_name]
        if  message.text in get_video_clips_names:
            userInfo[str(message.chat.id)+'_get_video_clips_names']=message.text
        if message.text == '/stop': stop(message); return
        if (message.text == 'Вернуться к выбору каталога'):back(message); return
        if message.text == '/about': about(message)
        if message.text == '/contacts': contacts(message)
        if message.text == '/start': stop(message); return
        if (message.text == 'Использовать тоже фото'):
            bot.send_photo(chat_id=message.chat.id, photo=userInfo[str(message.chat.id)+'_photo'], caption='Будет использовано это фото')
            userInfo[str(message.chat.id)+'_step'] = 'get_previous_photo'
            save_result(message)
        elif (message.content_type == 'photo' and userInfo[str(message.chat.id)+'_step'] == 'get_photo'):
            userInfo[str(message.chat.id)+'_photo'] = (message.photo[-1].file_id)
            save_result(message)
        elif userInfo[str(message.chat.id)+'_step'] == 'get_clip_name' and userInfo[str(message.chat.id)+'_get_video_clips_names'] in get_video_clips_names \
            or userInfo[str(message.chat.id)+'_step'] == 'get_photo' and userInfo[str(message.chat.id)+'_get_video_clips_names'] in get_video_clips_names:
            userInfo[str(message.chat.id)+'_choose'] = message.text
            userInfo[str(message.chat.id)+'_step'] = 'get_photo'
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
            # return
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
    userInfo[str(message.chat.id)+'_record_date'] = pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S')
    tg_user_id=message.from_user.id
    if userInfo[str(message.chat.id)+'_photo'] and userInfo[str(message.chat.id)+'_step'] == 'get_previous_photo':
        downloaded_photo = userInfo[str(message.chat.id)+'_photo']
    else:
        letters = string.ascii_lowercase
        rnd_string = ''.join(random.choice(letters) for i in range(4))
        file_info = bot.get_file(userInfo[str(message.chat.id)+'_photo'])
        downloaded_photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, 'Ваши данные приняты.\n \
        Видео ' + str(userInfo[str(message.chat.id)+'_choose']) + ' формируется от 5 минут, в зависимости от нагрузки на сервис', \
        reply_markup=ReplyKeyboardRemove())
    userInfo[str(message.chat.id)+'_step'] = 'wait_video'

    try:
        mysqlfunc.insert_photos(downloaded_photo, tg_user_id, userInfo[str(message.chat.id)+'_record_date'])
        try:
            mysqlfunc.insert_user_data(userInfo[str(message.chat.id)+'_First_name'],userInfo[str(message.chat.id)+'_Last_Name'] \
                , downloaded_photo , tg_user_id,userInfo[str(message.chat.id)+'_choose'],userInfo[str(message.chat.id)+'_record_date'])
            mysqlfunc.set_status(tg_user_id,'ready_to_render',userInfo[str(message.chat.id)+'_record_date'])
        except Exception as err:
            print(f"Ошибка на стадии сохранения в таблицу users err: {err}")
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