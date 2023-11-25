import requests,os
import logging, logging.handlers
from datetime import datetime, date
from urllib.parse import urlparse
from libs import config as configs
from libs import mysql as mysqlfunc

BASE_URL = 'https://ilkarvet.ru/tg-ai-bot/rest/v1'
count=0

def send_message(chat_id,message):
    url = f'{BASE_URL}/send_message'
    headers = {'Content-Type': 'application/json'}
    
    data = {"chat_id": chat_id,"message": message}
    r = requests.post(url, json=data,headers=headers)
    return(r.status_code)

if __name__=='__main__':
        try:
            count=0
            language_codes=['ru','en']
            new_video='Films->Spider-Peters-New-Powers(ENG)'
            message_ru= f'''
            🌟 Добрый день! 🌟

Мы рады сообщить, что у нас появилось новое видео {new_video}! 😊🚀

🎬 Название: {new_video}

Обязательно загляните и насладитесь этим захватывающим контентом! 🌌😃
            '''

            message_eng= '''
           🌟 Good day! 🌟

We're excited to announce that we've released a new {new_video}! 😊🚀

🎬 Title: {new_video}

Be sure to check it out and enjoy this thrilling content! 🌌😃
            '''
            for language_code in language_codes:
                if language_code=='ru':
                    message=message_ru
                else:
                    message=message_eng
                tg_users_ids=mysqlfunc.get_users_notification(language_code)
                # print(tg_users_ids)
                # for tg_user_id in tg_users_ids:
                #     print(tg_user_id['tg_user_id'])
                # tg_users_ids=[ {'tg_user_id': '673623552'},{'tg_user_id': '166889867'}]
                for tg_user_id in tg_users_ids:
                    status=send_message(tg_user_id['tg_user_id'],message)
                if status==200:
                    count+=1
                print(f" Отправленно {count} оповещений пользователям")
        except Exception as e:
             print(e)