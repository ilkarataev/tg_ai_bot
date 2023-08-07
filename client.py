
import traceback
import random
from telebot import types
from libs import config as configs
from libs import mysql as mysqlfunc
from libs import yandex_libs as yalib
from libs import additional_func as adf
from datetime import datetime
import requests
from datetime import datetime, date, time
import sys
import re
 
# bot = telebot.TeleBot(configs.bot_token);
# 1. Поиск таски выдергивание tguserid
# 3. Сохранения в папку фото
# 4. Изменить статус на редер 
# 4. Рендер 
# 5. Видео файл проверить что существует и место >1mb
#
# 5. Отправка видео куда-то думаю сразу в ТГ с компа с рендером 
#Изменить статус на compleate
# 6. Очистка удаление 
def get_photo():    
     print("asdasd")
     
# ../root_cam/run.py
if __name__=='__main__':
    # while True:
        try:
            # sleep(30)
            tg_user_id=get_task();
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            # bot.send_message(, f'{configs.stage} {e} --------- {trace}')
            print(f'{configs.stage} {e} --------- {trace}')
            time.sleep(3)
 