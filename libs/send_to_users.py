import requests,os
import logging, logging.handlers
from datetime import datetime, date
from urllib.parse import urlparse
from libs import config as configs
from libs import mysql as mysqlfunc

BASE_URL = 'https://ilkarvet.ru/tg-ai-bot/rest/v1'
count=0

def send_message(chat_id, message):
    url = f'{BASE_URL}/send_message'
    headers = {'Content-Type': 'application/json'}
    
    data = {"chat_id": chat_id,"message": message}
    r = requests.post(url, json=data,headers=headers)
    return(r.status_code)

def send_notification(language_code='', message='', type='new_video'):
        try:
            # 'Films->Spider-Peters-New-Powers(ENG)'
            if type=='new_video':
                print('new_video')
                new_video=message
                if language_code=='':
                    language_codes=['ru','en']
                else:
                    language_codes=[language_code]
                message_ru= f'''
                🌟 Добрый день! 🌟

    Мы рады сообщить, что у нас появилось новое видео {new_video}! 😊🚀

    🎬 Название: {new_video}

    Обязательно загляните и насладитесь этим захватывающим контентом! 🌌😃
                '''

                message_eng= f'''
            🌟 Good day! 🌟

    We're excited to announce that we've released a new {new_video}! 😊🚀

    🎬 Title: {new_video}

    Be sure to check it out and enjoy this thrilling content! 🌌😃
                '''
            elif type=='' or type==None:
                 message_ru=message
                 message_eng=message
                 language_codes=[language_code]
            counts = {}
            count_summ = 0
            for language_code in language_codes:

                if language_code=='ru':
                    message=message_ru
                else:
                    message=message_eng

                tg_users_ids=mysqlfunc.get_users_notification(language_code)

                # Инициализация счетчика для текущего language_code
                counts[language_code] = 0
                #for test
                # tg_users_ids=[{'tg_user_id': '166889867'}]
                print(tg_users_ids)
                for tg_user_id in tg_users_ids:
                    status=send_message(tg_user_id['tg_user_id'],message)
                    if status==200:
                        counts[language_code] += 1
                        count_summ += 1

            for language_code, count in counts.items():
                print(f"Отправлено {count} оповещений пользователям с {language_code} языком")

            print(f"Всего отправлено {count_summ} оповещений")

            return True, count_summ
        except Exception as e:
             print(f"Ошибка в функции send_notification")
             print(e)
             return False