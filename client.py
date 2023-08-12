import re,os.path,shutil,time,yadisk,subprocess,tempfile
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
import requests,time
from datetime import datetime, date
import sys
import re

bot = telebot.TeleBot(configs.bot_token);
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
BASE_URL = 'http://127.0.0.1:5000/rest/v1'
print(1)

def get_task():
    url = f'{BASE_URL}/get_task_to_render'
    response = requests.get(url)
    if response.status_code == 200:
        task = response.json()
        print(2)
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
        # Check if the input_face.png file exists
        if os.path.exists(file_path):
            print(f'Photo saved successfully to {file_path}')
        else:
            print(f'Error: The input_face.png file does not exist at path: {file_path}')
    else:
        # Handle the error
        print(f'Backend return a error {response.status_code}')


# меняем статус запускаем прогу и проверяем результат 
def set_status_rendering(tg_user_id, clip_name, render_host):

    # response = requests.get(f'{BASE_URL}/get_task_to_render')
    # data = response.json()
    # tg_user_id = data['tg_user_id']
    # clip_name = data['clip_name']


    # Check if the Roop folder exists
    roop_path = os.path.join(os.getcwd(), 'Roop')
    if not os.path.exists(roop_path):
        print(f"Roop папки не существует по пути: {roop_path}")
        sys.exit()

    # Set up the virtual environment
    # pypath = os.path.join(os.getcwd(),'Roop\\python')
    # venvpath = os.path.join(os.getcwd(), 'Roop\\venv')
    
    # Set environment variables
    os.environ['appdata'] = 'tmp'
    os.environ['userprofile'] = 'tmp'
    os.environ['temp'] = 'tmp'
    os.environ['path'] = 'git\cmd;python;venv\scripts;ffmpeg'
    os.environ['cuda_path'] = 'venv\\Lib\\site-packages\\torch\\lib'
    
    # Run the Python script without activating the virtual environment
    temp_dir = tempfile.gettempdir()
    subprocess_folder=os.path.join(os.getcwd(),'Roop\\')
    media_path=os.path.join(os.getcwd(), 'media')
    
    # Use the retrieved clip_name when constructing the path to the video file
    video_path = os.path.join(media_path, f'{clip_name}.mp4')
    if os.path.basename(video_path) == clip_name + '.mp4':
        print("Start rendring")
        start_time = time.time()  # Start the timer
        # Proceed with rendering only if the video_path matches the clip_name
        render_process=subprocess.run(['Roop\\python\\python.exe', 'run.py', '--execution-provider', 'cuda', '--source', f'{temp_dir}\\input_face.png', '--target',  video_path, '--output', f'{media_path}\\output.mp4', '--keep-fps'],cwd=subprocess_folder)
        render_process.wait()
        end_time = time.time()  # Stop the timer
        render_time = int(end_time - start_time)  # Calculate the time delta in seconds
        url = f'{BASE_URL}/set_rendering_duration'
        data = {'tg_user_id': tg_user_id, 'duration_seconds': render_time, 'render_host': render_host}
        response = requests.post(url, json=data)
    else:
        print("Error: video_path does not match clip_name")
        sys.exit(1)
def set_status_complete(tg_user_id):
    if set_status_rendering(tg_user_id):
        url = f'{BASE_URL}/set_status'
        data = {'tg_user_id': tg_user_id, 'status': 'complete'}
        response = requests.post(url, json=data)
    
        print('Status updated successfully to complete')
        # Check if the output file exists and has a size greater than 1 MB
        output_file_path = os.path.join(media_path, 'output.mp4')
        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 1e6:
            print('Output file exists and has a size greater than 1 MB')
        else:
            print('Output file does not exist or has a size less than or equal to 1 MB')
    else:
        # Handle the error
        print(f'An error occurred: {response.status_code}')


# отправляем видео

# def send_video(chat_id):
    
#     media_path = os.path.join(os.getcwd(), 'media')
#     video_path = os.path.join(media_path, 'output.mp4')
#     with open(video_path, 'rb') as video_file:
#         bot.send_video(chat_id, video_file)
#     print(f'Video sent successfully from {video_path}')

# удаляем отработанное
def delete_files():
    temp_dir = tempfile.gettempdir()
    media_path = os.path.join(os.getcwd(), 'media')
    input_face_path = os.path.join(temp_dir, 'input_face.png')
    face_video_path = os.path.join(media_path, 'output.mp4')
    try:
        os.remove(input_face_path)
        os.remove(face_video_path)
        print(f'Files deleted successfully from {temp_dir} and {media_path}')
    except OSError as e:
        # Handle the error
        print(f'An error occurred: {e}')

if __name__=='__main__':
    while True:
        try:
            #вызываем get_task
            response = get_task()
            print(response)
            print(type(response))
            if response:
                tg_user_id = response['tg_user_id']
                clip_name = response['clip_name']
                get_photo(tg_user_id)
                render_host ="imya_mashini"
                set_status_rendering(tg_user_id, clip_name, render_host)
                # send_video(chat_id)
                #set_status_complete(tg_user_id)
                #delete_files() 
            time.sleep(10)
            # tg_user_id=get_task_to_render();
        except Exception as e:
            print(e)
            trace=traceback.print_exc()
            print(traceback.format_exc())
            # bot.send_message(, f'{configs.stage} {e} --------- {trace}')
            # print(f'{configs.stage} {e} --------- {trace}')
        time.sleep(10)
            
 