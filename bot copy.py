import re,os.path,shutil,time,yadisk
import traceback
import string,random,re
import random
import telebot
from telebot import types
from libs import config as configs
from libs import mysql as mysqlfunc
from libs import yandex_libs as yalib
from libs import additional_func as adf
from datetime import datetime
from libs import telebot_calendar as tbc
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from yoomoney import Client
from yoomoney import Quickpay
from pyvin import VIN
 
bot = telebot.TeleBot(configs.bot_token);
# yandex_disk = yadisk.YaDisk(token=configs.yandex_disk_token)
# ya_check_token=yandex_disk.check_token()
 

# if not ya_check_token:
#     err_text='Нужно обновить токен для доступа к яндексу'
#     print(err_text)
#     bot.send_message(configs.logs_chat, f'{configs.stage} {err_text}')
#     exit()
 
userInfo = {}
 
@bot.message_handler(content_types=['text'])
def start(message):
    userInfo[str(message.chat.id)+'_botState'] = False
    userInfo[str(message.chat.id)+'_photoMessage'] = ''
    userInfo[str(message.chat.id)+'_userID'] = message.from_user.id
    userInfo[str(message.chat.id)+'_step'] = ''
    userInfo[str(message.chat.id)+'_recod_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        if message.text == '/start' and not userInfo[str(message.chat.id)+'_botState']:
            userInfo[str(message.chat.id)+'_botState']=True;
            bot.send_message(message.from_user.id, adf.getStringFromDB(mysqlfunc.read_dialogs('text1'), ''), reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
            bot.send_message(message.from_user.id, adf.getStringFromDB(mysqlfunc.read_dialogs('text2'),''), parse_mode="HTML")
            keyboard = types.InlineKeyboardMarkup();
            key_yes = types.InlineKeyboardButton(text='Согласен', callback_data='yes_privacy');
            keyboard.add(key_yes);
            key_no= types.InlineKeyboardButton(text='Не согласен', callback_data='no_privacy');
            keyboard.add(key_no);
            question=mysqlfunc.read_dialogs('question1')
            bot.send_message(message.from_user.id, adf.getStringFromDB(question,''), reply_markup=keyboard)
        elif message.text == '/start' and userInfo[str(message.chat.id)+'_botState']:
            bot.send_message(message.from_user.id, 'Бот уже запущен')
        elif message.text == '/stop':
            userInfo[str(message.chat.id)+'_botState']=False
            bot.clear_step_handler_by_chat_id(message.from_user.id)
            bot.send_message(message.from_user.id, 'Бот остановлен перезапустите бота')
            if (botStop(message)): return
        elif message.text==mysqlfunc.read_dialogs('photo_btn'):
            get_final(message)
        elif not message.chat.id == configs.manager_chat or not message.chat.id == configs.logs_chat:
            bot.send_message(message.from_user.id,  'Для запуска бота нажми /start');
    except Exception as err:
        text=f'{configs.stage} : Ошибка функция {message},user {message.from_user.id} err: {err}'
        bot.send_message(configs.logs_chat, text)
        print(err)
 
def botStop(message):
    if message.content_type == 'text':
        if (message.text.lower() == '/stop'):
            userInfo[str(message.chat.id)+'_botState']=False
            bot.send_message(message.chat.id, 'Бот остановлен,данные не сохранены, для перезапуска бота /start')
            return True
 
def get_surname(message): #получаем фамилию
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        userInfo[str(message.chat.id)+'_surname'] = message.text.replace(" ", "").capitalize();
        bot.send_message(message.from_user.id, 'Укажите ваше имя (русская раскладка)');
        bot.register_next_step_handler(message, get_name);
        if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
            adf.dev_auto_btn(bot, types, message,'Тестер')
    else:
        bot.send_message(message.from_user.id,'Укажите вашу фамилию (русская раскладка)');
        bot.register_next_step_handler(message, get_surname);
 
def get_name(message): #получаем имя
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        userInfo[str(message.chat.id)+'_name'] = message.text.replace(" ", "").capitalize();
        bot.send_message(message.from_user.id, 'Укажите ваше отчество (русская раскладка)');
        bot.register_next_step_handler(message, get_patronymic);
        if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
            adf.dev_auto_btn(bot, types, message,'Тестерович')
    else:
        bot.send_message(message.from_user.id,'Укажите ваше имя (русская раскладка)');
        bot.register_next_step_handler(message, get_name);
 
def get_patronymic(message): #получаем отчество
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        userInfo[str(message.chat.id)+'_midName'] =  message.text.replace(" ", "").capitalize();
        bot.send_message(message.from_user.id,'Укажите ваш регион проживания');
        bot.register_next_step_handler(message, get_live_area);
        if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
            adf.dev_auto_btn(bot, types, message,'Челябинская область')
    else:
        bot.send_message(message.from_user.id,'Укажите ваше отчество (русская раскладка)');
        bot.register_next_step_handler(message, get_patronymic);
 
def get_live_area(message):
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_live_area = types.KeyboardButton(text='Совпадает с регионом проживания')
        keyboard.add(button_live_area)
        userInfo[str(message.chat.id)+'_liveArea'] = message.text.capitalize();
        bot.send_message(message.from_user.id,'Укажите регион, где произошло ДТП',reply_markup=keyboard);
        bot.register_next_step_handler(message, get_area);
    else:
        bot.send_message(message.from_user.id,'Укажите ваш регион проживания');
        bot.register_next_step_handler(message, get_live_area);
 
def get_area(message):
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        if message.text == 'Совпадает с регионом проживания':
            userInfo[str(message.chat.id)+'_area'] = userInfo[str(message.chat.id)+'_liveArea']
        else:
            userInfo[str(message.chat.id)+'_area'] = message.text.capitalize();
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,'Укажите город, где произошло ДТП',reply_markup=keyboard);
        bot.register_next_step_handler(message, get_city);
        if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
            adf.dev_auto_btn(bot, types, message,'Челябинск')
    else:
        bot.send_message(message.from_user.id,'Укажите регион, где произошло ДТП');
        bot.register_next_step_handler(message, get_area);
 
def get_city(message):
    if (botStop(message)): return
    if  adf.match_ru_text(str(message.text)) and message.content_type == 'text':
        userInfo[str(message.chat.id)+'_city'] = message.text.capitalize();
        bot.send_message(message.from_user.id,'Укажите гос номер вашего а/м в формате А123АА174 или А123АА74');
        bot.register_next_step_handler(message, get_car_number);
        if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
            adf.dev_auto_btn(bot, types, message,'о777оо174')
    else:
        bot.send_message(message.from_user.id,'Укажите город, где произошло ДТП');
        bot.register_next_step_handler(message, get_city);
 
def get_car_number(message):
    if (botStop(message)): return
    if message.content_type == 'text':
        userInfo[str(message.chat.id)+'_carNum'] = message.text.upper();
        match_car_number = bool(re.search(r'[а-яА-Яa-zA-Z]{1}\d{3}[а-яА-Яa-zA-Z]{2}\d{2,3}', userInfo[str(message.chat.id)+'_carNum']))
        if match_car_number:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(types.KeyboardButton(text='Отправлю позже фото СТС'))
            bot.send_message(message.from_user.id,'Укажите VIN код вашего автомобиля, или номер кузова.\n' \
            +'Можно отправить фото СТС, на этапе отправки фото о ДТП',reply_markup=keyboard);
            bot.register_next_step_handler(message, get_car_vin);
            if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
                keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                keyboard.add(types.KeyboardButton(text='Отправлю позже фото СТС'))
                keyboard.add(types.KeyboardButton(text='JT2AE09W4P0038539'))
                bot.send_message(message.from_user.id, 'Тестовый ответ, нажми на кнопку',reply_markup=keyboard);
        else:
            bot.send_message(message.from_user.id,'Повторите ввод номера а/м в формате А123АА174 или А123АА74');
            bot.register_next_step_handler(message, get_car_number);
    else:
        bot.send_message(message.from_user.id,'Повторите ввод номера а/м в формате А123АА174 или А123АА74');
        bot.register_next_step_handler(message, get_car_number);
def get_car_vin(message):
    if (botStop(message)): return
    if message.content_type == 'text':
        if message.text == 'Отправлю позже фото СТС':
            userInfo[str(message.chat.id)+'_car_model_from_vin']='Неопределена'
            userInfo[str(message.chat.id)+'_vin'] = 'Фото СТС';            
            bot.send_message(message.from_user.id,'Укажите ваш пробег цифрами',reply_markup=types.ReplyKeyboardRemove());
            bot.register_next_step_handler(message, get_car_run)
            if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
                adf.dev_auto_btn(bot, types, message,'120000')
        else:
            vin_code=message.text
            if not vin_code.isnumeric():
                vehicle = VIN(vin_code)
            else:
                vehicle = False
            if bool(vehicle):
                keyboard=adf.yes_no_keyboardkeyboard(types)
                car_model_from_vin=f'Это ваша машина \n марка: {vehicle.Make}, \n Модель: {vehicle.Model}, \n год выпуска: {vehicle.ModelYear}'
                bot.send_message(message.from_user.id, car_model_from_vin, reply_markup=keyboard)
                bot.register_next_step_handler(message, get_car_vin_check, car_model_from_vin, vin_code);
            elif not bool(vehicle):
                keyboard=adf.yes_no_keyboardkeyboard(types)
                bot.send_message(message.from_user.id, f'Мы не нашли этот "{message.text}" VIN код в базе, он правильный?', reply_markup=keyboard)
                bot.register_next_step_handler(message,get_car_vin_check,'',vin_code);
 
def get_car_vin_check(message,car_model_from_vin,vin_code):
        userInfo[str(message.chat.id)+'_car_model_from_vin']='Неопределена'
        if (message.content_type == 'text' and message.text == 'Да'):
            userInfo[str(message.chat.id)+'_vin'] = vin_code;
            if car_model_from_vin != '':
                userInfo[str(message.chat.id)+'_car_model_from_vin'] = car_model_from_vin;
            bot.send_message(message.from_user.id,'Укажите ваш пробег цифрами',reply_markup=types.ReplyKeyboardRemove());
            bot.register_next_step_handler(message, get_car_run);
            if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
                adf.dev_auto_btn(bot, types, message,'120000')
        elif (message.content_type == 'text' and message.text == 'Нет'):
            bot.send_message(message.from_user.id,'Укажите VIN код вашего автомобиля',reply_markup=types.ReplyKeyboardRemove());
            bot.register_next_step_handler(message, get_car_vin);
        else:
            keyboard=adf.yes_no_keyboardkeyboard(types)
            bot.send_message(message.from_user.id, 'Ответьте Да или Нет', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_car_vin_check, car_model_from_vin, vin_code);
 
 
def get_car_run(message):
    if (botStop(message)): return
    userInfo[str(message.chat.id)+'_uts'] = 'Нет'
    if message.text.isdigit() and message.content_type == 'text':
        userInfo[str(message.chat.id)+'_carRun'] = int(message.text)
        if (int(userInfo[str(message.chat.id)+'_carRun']) < 100000):
            keyboard=adf.yes_no_keyboardkeyboard(types)
            bot.send_message(message.chat.id, 'Являлся ли ваш автомобиль участником ДТП ранее с оформлением в ГАИ', reply_markup=keyboard)
            bot.register_next_step_handler(message, ifDtp)
            return 
        now = datetime.now()
        bot.send_message(
            message.chat.id,
             "Выберите дату ДТП",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),
        )
    else:
        bot.send_message(message.from_user.id, 'Пробег нужно указать цифрами и без пробелов');
        bot.register_next_step_handler(message, get_car_run);
 
def ifDtp(message):
    if (botStop(message)): return
    if (message.text.lower() == 'да'):
        now = datetime.now()
        bot.send_message(
            message.chat.id,
             "Выберите дату ДТП",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),
        )
        # if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
        #     bot.send_message(message.chat.id, '2008-11-02')
    elif (message.text.lower() == 'нет'):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        russian = types.KeyboardButton(text='Отечественное авто')
        notRussian = types.KeyboardButton(text='Иностранное авто')
        keyboard.add(russian)
        keyboard.add(notRussian)
        bot.send_message(message.chat.id, 'Выберете страну производителя?', reply_markup=keyboard)
        bot.register_next_step_handler(message, getCarProd)
    else: 
        bot.send_message(message.chat.id, 'Выберите ответ (Да/Нет)')
        bot.register_next_step_handler(message, ifDtp)
 
def getCarProd(message):
    if (botStop(message)): return
    if (message.text.lower() == 'иностранное авто'):
        keyboard=adf.yes_no_keyboardkeyboard(types)
        bot.send_message(message.chat.id, 'Ваше авто старше 5-ти лет?', reply_markup=keyboard)
        bot.register_next_step_handler(message, getAns1)
    elif (message.text.lower() == 'отечественное авто'):
        keyboard=adf.yes_no_keyboardkeyboard(types)
        bot.send_message(message.chat.id, 'Ваше авто старше 3-x лет?', reply_markup=keyboard)
        bot.register_next_step_handler(message, getAns1 )
    else:
        bot.send_message(message.chat.id, 'Выберете страну производителя?')
        bot.register_next_step_handler(message, getCarProd)
 
def getAns1(message):
    if (botStop(message)): return
 
    if (message.text.lower() == 'нет'):
        userInfo[str(message.chat.id)+'_uts'] = 'Да'
    elif (message.text.lower() != 'да'):
        bot.send_message(message.chat.id, 'Выберите ответ (Да/Нет)')
        bot.register_next_step_handler(message, getAns1)
        return
 
    now = datetime.now()
    bot.send_message(
        message.chat.id,
            "Выберите дату ДТП",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,  # Specify the NAME of your calendar
        ),
    )
 
def get_dtp_date(message):
    if (botStop(message)): return
    if message.content_type == 'text':
        if bool(re.search(r'\d{4}-\d{2}-\d{2}', message.text)):
            userInfo[str(message.chat.id)+'_dtpDate'] = message.text;
            # check not earrlier than today
            past = datetime.strptime(userInfo[str(message.chat.id)+'_dtpDate'], "%Y-%m-%d")
            present = datetime.now()
            if past.date() <= present.date():
                bot.send_message(message.from_user.id,'Укажите вашу электронную почту, в формате example@gmail.com');
                bot.register_next_step_handler(message, get_email);
                if configs.stage == 'DEV' or message.from_user.id == 166889867 or message.from_user.id == 673623552:
                    adf.dev_auto_btn(bot, types, message,'test@gmail.com')
            else:
                bot.send_message(message.from_user.id,'Дата дтп не может быть в будущем');
                now = datetime.now()  # Get the current date
                bot.send_message(
                    message.chat.id,
                    "Выберите дату ДТП",
                    reply_markup=calendar.create_calendar(
                        name=calendar_1_callback.prefix,
                        year=now.year,
                        month=now.month,  # Specify the NAME of your calendar
                    ),
                )
        else:
            bot.send_message(message.from_user.id,'Укажите дату ДТП в формате год-месяц-день к примеру 2022-06-01');
            bot.register_next_step_handler(message, get_dtp_date);
    else:
        bot.send_message(message.from_user.id,'Укажите дату ДТП в формате год-месяц-день к примеру 2022-06-01');
        bot.register_next_step_handler(message, get_dtp_date);
 
def get_email(message):
    if (botStop(message)): return
    if message.content_type == 'text':
        if bool(re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+',message.text.replace(" ", ""))):
            userInfo[str(message.chat.id)+'_email'] = message.text;
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_phone = types.KeyboardButton(text="Отправить номер из аккаунта телеграмма", request_contact=True)
            noPhone = types.KeyboardButton(text="Не указывать")
            keyboard.add(button_phone)
            keyboard.add(noPhone)
            userInfo[str(message.chat.id)+'_step'] = 'get_phone_number';
            bot.send_message(message.from_user.id,'Укажите номер мобильного телефона в формате +77777777 или отправьте из контактов (Не обязательно)',reply_markup=keyboard);
            bot.register_next_step_handler(message, get_phone_number);
        else:
            bot.send_message(message.from_user.id,'Вы неверно ввели почту');
            bot.send_message(message.from_user.id,'Укажите вашу электронную почту, в формате example@gmail.com');
            bot.register_next_step_handler(message, get_email);
    else:
        bot.send_message(message.from_user.id,'Вы неверно ввели почту');
        bot.send_message(message.from_user.id,'Укажите вашу электронную почту, в формате example@gmail.com');
        bot.register_next_step_handler(message, get_email);
 
def get_phone_number(message):
    if (botStop(message)): return
    if message.content_type == 'text':
        if (message.text.lower() == 'не указывать'):
            userInfo[str(message.chat.id)+'_pNumber'] = 'Не указан';
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_skip = types.KeyboardButton(text='Пропустить')
            keyboard.add(button_skip)
            bot.send_message(message.chat.id, 'В следующем сообщение вы можете добавить дополнительную информацию', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_notice)
            return
        if bool(re.search(r'^\+7\d{3}\d{3}\d{4}$', message.text.replace(" ", ""))):
            userInfo[str(message.chat.id)+'_pNumber'] = message.text;
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_skip = types.KeyboardButton(text='Пропустить')
            keyboard.add(button_skip)
            bot.send_message(message.chat.id, 'В следующем сообщение вы можете добавить дополнительную информацию', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_notice);
        else:
            bot.send_message(message.from_user.id,'Введенный вами номер не соответствует формату +77777777777, попробуйте еще раз');
            bot.register_next_step_handler(message, get_phone_number);
    elif message.content_type =='contact':
        contact(message)
 
def get_notice(message):
    if (botStop(message)): return
    userInfo[str(message.chat.id)+'_notice']=message.text;
    # keyboard = types.ReplyKeyboardRemove()
    userInfo[str(message.chat.id)+'_photoList'] = []
    userInfo[str(message.chat.id)+'_step'] = 'get_photo'
    userInfo[str(message.chat.id)+'_text_photo_one_more'] = mysqlfunc.read_dialogs('photo_one_more');
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_photo_stop = types.KeyboardButton(text=mysqlfunc.read_dialogs('photo_btn'))
    keyboard.add(button_photo_stop)
    bot.send_message(message.chat.id, 'Теперь необходимо загрузить фотографии',reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, mysqlfunc.read_dialogs('text_photo_dtp'),reply_markup=keyboard)
    bot.register_next_step_handler(message, photo_handler);
 
def get_final(message):
    if (botStop(message)): return
    count=0
    tg_user_id=message.from_user.id;
    surname = userInfo[str(message.chat.id)+'_surname']
    name = userInfo[str(message.chat.id)+'_name']
    patronymic = userInfo[str(message.chat.id)+'_midName']
    email = str(userInfo[str(message.chat.id)+'_email'])
 
    if len(userInfo[str(message.chat.id)+'_photoList']) >= 1:
            keyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, 'Фотографии полученны, ожидайте обработки данных', reply_markup=keyboard)
            question = 'ФИО: \n' +surname+ '\n' +name+ '\n' +patronymic+' \nАдрес проживания: \n' \
            +userInfo[str(message.chat.id)+'_liveArea']+ '\nГород в котором произошло ДТП: \n' \
            +userInfo[str(message.chat.id)+'_city'] + '\nРегион в котором произошло ДТП: \n' \
            +userInfo[str(message.chat.id)+'_area']+ '\nНомер вашего а/м: \n' \
            +userInfo[str(message.chat.id)+'_carNum']+ '\nVIN код а/м: \n' \
            +str(userInfo[str(message.chat.id)+'_vin']) +'\nПробег а/м: \n' \
            +str(userInfo[str(message.chat.id)+'_carRun'])  \
            +'\nДата ДТП: \n' + str(userInfo[str(message.chat.id)+'_dtpDate']) \
            +'\nКонтактные данные: \nemail: \n' +email+ '\nтелефоный номер: \n' \
            +str(userInfo[str(message.chat.id)+'_pNumber']) \
            +'\nДополнительная информация: \n' + str(userInfo[str(message.chat.id)+'_notice']) \
            +'\nУТС: \n' + str(userInfo[str(message.chat.id)+'_uts']) \
            +'\nИнформация из VIN кода: \n' + str(userInfo[str(message.chat.id)+'_car_model_from_vin']);
            if configs.stage == 'PROD':
                #create local path store photo and text
                today = datetime.now().strftime("%Y-%m-%d")
                letters = string.ascii_lowercase
                rnd_string = ''.join(random.choice(letters) for i in range(4))
                parent_dir = "/Telegram_bot/"
                # createPath
                sub_path_name=f'{surname}_{name}_{patronymic}_{email}_{today}_{rnd_string}'
                path = os.path.join(f'.{parent_dir}', sub_path_name)
                if not os.path.isdir(path):
                    os.makedirs(path)
                with open(path + '/' + str(tg_user_id) + '_' + str(count) + ".txt", 'w') as new_file_text:
                    new_file_text.write(question)
                for x_photo in userInfo[str(message.chat.id)+'_photoList']:
                    bot.send_photo(configs.manager_chat, photo=x_photo)
                    #get photo prom tg
                    file_info = bot.get_file(x_photo)
                    downloaded_photo = bot.download_file(file_info.file_path)
                    try:
                        count+=1
                        # save photo
                        with open(path + '/' + str(tg_user_id) + '_' + str(count) + ".jpg", 'wb') as new_file:
                            new_file.write(downloaded_photo)
                        #save photo to mysql
                        mysqlfunc.insert_photos(downloaded_photo, tg_user_id, userInfo[str(message.chat.id)+'_recod_date'])
                    except Exception as err:
                        text=f'{configs.stage} : Ошибка на стадии сохранения фото {message},user {message.from_user.id} err: {err}'
                        bot.send_message(configs.logs_chat, text)
                        print(err)
                        print("save photo problem")
                #copy photo to yandex
                try:
                        yalib.recursive_upload_yandex(yandex_disk, f".{parent_dir}", f"{parent_dir}")
                except Exception as err:
                        text=f'{configs.stage} : Ошибка yandex save {message},user {message.from_user.id} err: {err}'
                        bot.send_message(configs.logs_chat, text)
                        print(err)
                shutil.rmtree(f'.{parent_dir}{sub_path_name}',ignore_errors=False, onerror=None)
            #send text after photos to manager chat
            bot.send_message(configs.manager_chat, text=question, reply_markup=keyboard)
            bot.send_message(message.chat.id, text=question)
            worker_final(message)
#######################################################################################handlers
@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.content_type == 'contact' and userInfo[str(message.chat.id)+'_step'] == 'get_phone_number':
        if bool(re.search('^\+7[0-9]{10}',message.contact.phone_number)):
            userInfo[str(message.chat.id)+'_pNumber']=message.contact.phone_number
        elif bool(re.search('^8[0-9]{10}',message.contact.phone_number)):
            userInfo[str(message.chat.id)+'_pNumber']=re.sub("^8", "+7",message.contact.phone_number)
        elif bool(re.search('^7[0-9]{10}',message.contact.phone_number)):
            userInfo[str(message.chat.id)+'_pNumber']='+' + message.contact.phone_number
        else:
            userInfo[str(message.chat.id)+'_pNumber']=message.contact.phone_number
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_skip = types.KeyboardButton(text='Пропустить')
        keyboard.add(button_skip)
        bot.send_message(message.chat.id, 'В следующем сообщение вы можете добавить дополнительную информацию', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_notice);
    elif userInfo[str(message.chat.id)+'_step'] == 'get_phone_number':
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Ваш номер не содержиться в контактах, нужно добавить его в ручную в формате +77777777', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_phone_number);
    else:
        message.text='start'
        start(message)
 
 
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
 
    if (message.content_type == 'text' and botStop(message)): return
    if userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'photo':
        if not message.photo[-1].file_id in userInfo[str(message.chat.id)+'_photoList']:
            userInfo[str(message.chat.id)+'_photoList'].append(message.photo[-1].file_id)
        # text=userInfo[str(message.chat.id)+'_text_photo_one_more'];
        # обработка решает проблему отправки сообщений когда отправляется несколько фото. нужно подумать как сделать по другому.
        # if userInfo[str(message.chat.id)+'_photoMessage'] != userInfo[str(message.chat.id)+'_text_photo_one_more']:
        #   userInfo[str(message.chat.id)+'_photoMessage']=text
        # bot.update.message.reply_text('How can I help?', reply_markup=reply_markup)
        # if userInfo[str(message.chat.id)+'_count_photo'] > 1 :
        #     bot.edit_message_text(text,message.chat.id,message.message_id)
        # else:
        #     bot.send_message(message.chat.id,text,reply_markup=keyboard);
        # userInfo[str(message.chat.id)+'_count_photo']=userInfo[str(message.chat.id)+'_count_photo']+1
    elif userInfo[str(message.chat.id)+'_step'] == 'get_photo' and message.content_type == 'text':
        bot.send_message(message.chat.id, 'Вам необходимо загрузить фотографии')
        bot.send_message(message.chat.id, mysqlfunc.read_dialogs('text_photo_dtp'))
        bot.register_next_step_handler(message, photo_handler);
    else:
        message.text='start'
        start(message)
 
@bot.callback_query_handler(func=lambda call: call.data == 'yes_privacy')
def callback_worker(call):
        if call.message.from_user.id != call.message.chat.id:
            call.message.from_user.id=call.message.chat.id
        bot.edit_message_text('Вы приняли условия работы с ботом. \n',call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id, "Укажите вашу фамилию (русская раскладка)");
        bot.register_next_step_handler(call.message, get_surname);
        if configs.stage == 'DEV' or call.message.chat.id == 166889867 or call.message.chat.id == 673623552:
            adf.dev_auto_btn(bot, types, call.message,'Тестеров')
 
@bot.callback_query_handler(func=lambda call: call.data == 'no_privacy')
def callback_worker(call):
        userInfo[str(call.message.chat.id)+'_botState']=False;
        bot.edit_message_text('Мы не можем продолжить пока вы не примете условия.\nБот будет перезапущен через 5 секунд',call.message.chat.id,call.message.message_id)
        time.sleep(5)
        call.message.text='/start'
        if call.message.from_user.id != call.message.chat.id:
            call.message.from_user.id=call.message.chat.id
        start(call.message)
 
def worker_final(message):
    if userInfo[str(message.chat.id)+'_uts'] == 'ДА':
        uts=True
    else:
        uts=False
    mysqlfunc.insert_user_data(userInfo[str(message.chat.id)+'_userID'],
        userInfo[str(message.chat.id)+'_name'], userInfo[str(message.chat.id)+'_midName'],
        userInfo[str(message.chat.id)+'_surname'], userInfo[str(message.chat.id)+'_area'],
        userInfo[str(message.chat.id)+'_city'], userInfo[str(message.chat.id)+'_liveArea'],
        userInfo[str(message.chat.id)+'_carNum'], userInfo[str(message.chat.id)+'_vin'],
        userInfo[str(message.chat.id)+'_carRun'], userInfo[str(message.chat.id)+'_dtpDate'],
        userInfo[str(message.chat.id)+'_email'], userInfo[str(message.chat.id)+'_pNumber'],
        userInfo[str(message.chat.id)+'_notice'], uts, False, userInfo[str(message.chat.id)+'_recod_date'])
    userInfo[str(message.chat.id)+'_payCode'] = str(message.chat.id) + str(round(time.time() * 1000))
    quickpay = Quickpay(
            receiver=configs.ym_receiver,
            quickpay_form="shop",
            targets="pay for dtp rating",
            paymentType="SB",
            sum=str(configs.ym_service_price),
            label=userInfo[str(message.chat.id)+'_payCode']
            )
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    yesBtn = types.KeyboardButton(text='Оплатил')
    keyboard.add(yesBtn)
    bot.send_message(message.chat.id, '<a href="'+quickpay.base_url+'">Оплатить</a>' \
        +'\nПосле оплаты нажмите "Оплатил"', parse_mode="HTML",reply_markup=keyboard);
    # print(quickpay.base_url)
    # print('<a href="'+quickpay.base_url+'">Оплатить</a>')
    # bot.send_message(message.chat.id, 'После оплаты нажмите "Оплатил"');
    bot.register_next_step_handler(message, checkPay)
 
def checkPay(message):
    if (botStop(message)): return
    if (message.text.lower() == 'оплатил'):
        history = Client(configs.ym_wallet_token).operation_history(label=str(userInfo[str(message.chat.id)+'_payCode']))
        for operation in history.operations:
            if (operation.status.lower() == 'success'):
                mysqlfunc.payment_success(message.chat.id, userInfo[str(message.chat.id)+'_dtpDate'], userInfo[str(message.chat.id)+'_recod_date'])
                bot.send_message(message.chat.id, adf.getStringFromDB(mysqlfunc.read_dialogs('text_final1'), ''),reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
                bot.send_message(message.chat.id, adf.getStringFromDB(mysqlfunc.read_dialogs('text_final2'), ''), parse_mode="HTML")
                userInfo[str(message.chat.id)+'_botState']=False;
                return
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        yesBtn = types.KeyboardButton(text='Оплатил')
        keyboard.add(yesBtn)
        bot.send_message(message.chat.id, 'Оплата еще не прошла. Попробуйте проверить позднее', reply_markup=keyboard);
        bot.register_next_step_handler(message, checkPay)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        yesBtn = types.KeyboardButton(text='Оплатил')
        keyboard.add(yesBtn)
        bot.send_message(message.chat.id, 'Неизвестная команда.', reply_markup=keyboard);
        bot.register_next_step_handler(message, checkPay)
 
#calendar
@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """
 
    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        user_date=f"{date.strftime('%Y-%m-%d')}"
        msg=bot.send_message(
            chat_id=call.from_user.id,
            text=user_date,
            reply_markup=ReplyKeyboardRemove(),
        )
        if call.message.from_user.id != call.message.chat.id:
            call.message.from_user.id=call.message.chat.id
        call.message.text=user_date;
        get_dtp_date(call.message)
 
 
if __name__=='__main__':
    # while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            bot.send_message(configs.logs_chat, f'{configs.stage} {e} --------- {trace}')
            time.sleep(3)
 