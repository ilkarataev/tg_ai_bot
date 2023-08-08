import re,os.path,shutil,time,yadisk
import traceback
import string,random,re
import random
import telebot
from telebot import types
#from libs import config as configs
from libs import mysql as mysqlfunc
from libs import yandex_libs as yalib
from libs import additional_func as adf
from datetime import datetime
import requests
from datetime import datetime, date, time
import sys
import re
import base64

import subprocess
import tempfile
#bot = telebot.TeleBot(configs.bot_token);
# обьявить урл в переменную 
# определение ос в  закидывать папку темп глобально обьявить 
# 1. Поиск таски выдергивание tguserid
# 3. Сохранения в папку фото
# 4. Изменить статус на редер 
# 4. Рендер 
# 5. Видео файл проверить что существует и место >1mb
#
# 5. Отправка видео куда-то думаю сразу в ТГ с компа с рендером 
#Изменить статус на compleate
# 6. Очистка удаление 
#меняем здесь урл
BASE_URL = 'http://localhost:5000/rest/v1'

def get_task():
    url = f'{BASE_URL}/get_task_to_render'
    response = requests.get(url)
    if response.status_code == 200:
        task = response.json()
        # Process the task as needed
        return task
    else:
        # Handle the error
        print(f'An error occurred: {response.status_code}')
        return None

def get_photo(tg_user_id):
    url = f'{BASE_URL}/get_photo_to_render'
    data = {"tg_user_id": int(tg_user_id)}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, 'input_face.png')
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f'Photo saved successfully to {file_path}')
    else:
        # Handle the error
        print(f'An error occurred: {response.status_code}')
# меняем статус запускаем прогу и проверяем результат 
def set_status_rendering(tg_user_id):
    url = f'{BASE_URL}/set_status'
    data = {'tg_user_id': tg_user_id, 'status': 'rendering'}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print('Status updated successfully to rendering')
        # Run the runwithoutgui.py script
        subprocess.run(['C:\\tgai\\Roop\\run.cmd'])
    else:
        # Handle the error
        print(f'An error occurred: {response.status_code}')

def set_status_complete(tg_user_id):
    url = f'{BASE_URL}/set_status'
    data = {'tg_user_id': tg_user_id, 'status': 'complete'}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print('Status updated successfully to complete')
        # Check if the output file exists and has a size greater than 1 MB
        temp_dir = tempfile.gettempdir()
        output_file_path = os.path.join(temp_dir, 'face-videoinput.mp4')
        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 1e6:
            print('Output file exists and has a size greater than 1 MB')
        else:
            print('Output file does not exist or has a size less than or equal to 1 MB')
    else:
        # Handle the error
        print(f'An error occurred: {response.status_code}')

# отправляем видео

# def send_video(tg_user_id, bot_token):
#     bot = telebot.TeleBot(bot_token)
#     temp_dir = tempfile.gettempdir()
#     video_path = os.path.join(temp_dir, 'face-videoinput.mp4')
#     with open(video_path, 'rb') as video_file:
#         bot.send_video(tg_user_id, video_file)
#     print(f'Video sent successfully from {video_path}')

# удаляем отработанное
def delete_files():
    temp_dir = tempfile.gettempdir()
    input_face_path = os.path.join(temp_dir, 'input_face.jpg')
    face_video_path = os.path.join(temp_dir, 'face-videoinput.mp4')
    try:
        os.remove(input_face_path)
        os.remove(face_video_path)
        print(f'Files deleted successfully from {temp_dir}')
    except OSError as e:
        # Handle the error
        print(f'An error occurred: {e}')

if __name__=='__main__':
    # while True:
        try:
            #вызываем get_task
            tg_user_id = get_task()
            if tg_user_id is not None:
                get_photo(tg_user_id)
                #set_status_rendering(tg_user_id)
                #set_status_complete(tg_user_id)

            # sleep(30)

            # tg_user_id=get_task_to_render();
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            # bot.send_message(, f'{configs.stage} {e} --------- {trace}')
            # print(f'{configs.stage} {e} --------- {trace}')
            
 