import io, requests, time, pytz, sys,json
from libs import config as configs
from libs import mysql as mysqlfunc
from flask import Flask, request, jsonify, send_file
import threading
import schedule
import yadisk
translations_path=configs.translations_path
# from translate import Translator
yandex_disk = yadisk.YaDisk(token=configs.yandex_disk_token)
ya_check_token = yandex_disk.check_token()

if not ya_check_token:
    print('Нужно обновить токен для доступа к Яндекс.Диску')
    sys.exit(1)

# translator = Translator(to_lang="Russian")

utc_tz = pytz.timezone('UTC')
app = Flask(__name__)

data_list = []
rest_api_url = '/tg-ai-bot/rest/v1/'

@app.route(f'{rest_api_url}logs', methods=['POST'])
def create_log():
    if request.method == 'POST':

        hostname = request.form.get('hostname') or 'UnknownHostname'
        loglevel = request.form.get('levelname') or 'UnknownLevel'
        msg = request.form.get('msg') or 'UnknownMessage'

        log_msg = f"{hostname}-{loglevel}-{msg}"

        try:
            mysqlfunc.insert_log(log_msg)
            return jsonify({"message": "Log received"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to insert log: {str(e)}"}), 500

    else:
        return jsonify({"error": "Unsupported Media Type. Please send as application/json"}), 415


@app.route(f'{rest_api_url}ready', methods=['GET'])
def get_ready():
    return "ready"

@app.route(f'{rest_api_url}get_task_to_render', methods=['GET'])
def get_task_to_render():
    response=mysqlfunc.get_task_to_render()
    if(response):
        return response
    else:
        return "false"

@app.route(f'{rest_api_url}get_video_clips', methods=['GET'])
def get_video_clips():
    video_clips = mysqlfunc.get_video_clips_name()
    return jsonify(video_clips)

@app.route(f'{rest_api_url}set_rendering_duration', methods=['POST'])
def set_rendering_duration():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        render_time = data['render_time']
        record_date = data['record_date']

        response = mysqlfunc.update_render_time(tg_user_id, render_time, record_date)
        return response

@app.route(f'{rest_api_url}render_host_enabled', methods=['POST'])
def render_host_enabled():
    if request.method == 'POST':
        data = request.json
        response = mysqlfunc.render_host_enabled(data['render_host_hostname'])
        return jsonify(response)

@app.route(f'{rest_api_url}update_render_host', methods=['POST'])
def update_render_host_route():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        render_host = data['render_host']

        response = mysqlfunc.update_render_host(tg_user_id, render_host)
        return response


@app.route(f'{rest_api_url}get_photo_to_render', methods=['POST'])
def get_photo_to_render():
    tg_user_id=''
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        record_date = data['record_date']
        if (tg_user_id != ''):
            response_image=mysqlfunc.get_photo_to_render(tg_user_id,record_date)
            blob_file = io.BytesIO(response_image)
            return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name=str(tg_user_id)+'_photo')

@app.route(f'{rest_api_url}get_client_code', methods=['GET'])
def get_client():
    if request.method == 'GET':
        with open('client.py', 'rb') as file:
            client_code = file.read()
        blob_file = io.BytesIO(client_code)
        return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name='client.py')

@app.route(f'{rest_api_url}set_status', methods=['POST'])
def set_status():
    if request.method == 'POST':
        data = request.json
        record_date = data['record_date']
        tg_user_id = data['tg_user_id']
        status = data['status']
        if (tg_user_id != '' and status !=''):
            response=mysqlfunc.set_status(tg_user_id,status,record_date)
            return response

@app.route(f'{rest_api_url}send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
            data = request.json
            chat_id = data['chat_id']
            message = data['message']
            url = f'https://api.telegram.org/bot{configs.bot_token}/sendMessage'
            data = {'chat_id': chat_id,'text':message}
            r = requests.post(url, json=data)
            return "True"

@app.route(f'{rest_api_url}send_video', methods=['POST'])
def send_video_file():
    if request.method == 'POST':
        chat_id=request.form.get('chat_id')
        record_date=request.form.get('record_date')
        file_size=request.form.get('file_size')
        video_file = request.files['file']
        if 'ru' == mysqlfunc.get_language_code(chat_id):
            with open(f"{translations_path}ru.json", 'r', encoding='utf-8') as f:
                translations = json.load(f)
        else:
            with open(f"{translations_path}en.json", 'r', encoding='utf-8') as f:
                translations = json.load(f)
        keyboard = {
            "keyboard": [
                [translations["msg_restart"]],
                [translations["msg_support"]]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        final_message = translations["backend_final_msg"]
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        video_data = {
            'video': (video_file.filename, video_file, 'video/mp4')
        }
        if video_file:
            file_size_megabytes = int(file_size) / 1048576
            mysqlfunc.insert_final_clip_size(chat_id,record_date,round(file_size_megabytes))
        if file_size_megabytes < 50:
            url = f'https://api.telegram.org/bot{configs.bot_token}/sendVideo'
            data = {'chat_id': chat_id}
            r = requests.post(url, data=data, files=video_data)
            print(r)
            if (r.status_code == 200):
                url = f'https://api.telegram.org/bot{configs.bot_token}/sendMessage'
                data = {'chat_id': chat_id,'text':final_message,'reply_markup': keyboard}
                r = requests.post(url, json=data,headers=headers)
                return "True"
            else:
                print("Проблемы с отправкой файла в телеграмм " +str(r.status_code))
                print(r.content)
                # mysqlfunc.set_status(chat_id,"Проблемы с отправкой файла в телеграмм")
                return "False"

@app.route(f'{rest_api_url}set_render_host_status', methods=['POST'])
def set_render_host_status():
    if request.method == 'POST':
        data = request.json
        render_host_hostname = data['render_host_hostname']
        status = data['status']
        if (render_host_hostname != '' and status !='' ):
            current_time_utc = pytz.datetime.datetime.now(utc_tz)
            record_date=current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
            mysqlfunc.set_render_host_status(render_host_hostname,status,record_date)
            return "True"

def sync_yandex_clips_list():
    root_folder = "/ROOP/video_clips/"
    folders = yandex_disk.listdir(root_folder)
    ya_video_dirs = []

    for folder in folders:
        if folder['type'] == 'dir':
            path = folder['path']
            watermark_path = path + "/watermark"
            ya_video_dirs.append(watermark_path)

    for dir in ya_video_dirs:
        files=yandex_disk.listdir(dir)
        get_video_clips_name=mysqlfunc.get_video_clips_name()
        for item in files:
            found_ya_clip_in_db = False
            url = item['file']
            name_en=item['name'].split('.mp4')[0]
            category=item['path'].split('/')[3]
            remote_url=item['file']
            remote_md5=item['md5']
            for db_video_clips in get_video_clips_name:
                if name_en == db_video_clips['name_en']:
                    found_ya_clip_in_db = True
                    if db_video_clips['name_ru'] == '' or db_video_clips['name_ru'] == None or \
                        db_video_clips['path'] == None or db_video_clips['md5'] == None or \
                        db_video_clips['url'] == None or db_video_clips['category'] == None:
                            found_ya_clip_in_db= False
                    if remote_url != db_video_clips['url']:
                            found_ya_clip_in_db= False
                    if remote_md5 != db_video_clips['md5']:
                            found_ya_clip_in_db= False

            if not found_ya_clip_in_db:
                try:
                    # name_ru = translator.translate(name_en)
                    name_ru = name_en
                except:
                    name_ru = name_en
                mysqlfunc.set_video_clips(name_en,name_ru,item['file'],item['path'],item['md5'],category)
        #Удаляем из бд записи если файлов уже нет в яндексе
        get_video_clips_name=mysqlfunc.get_video_clips_name('path')
        for db_video_clip_path in get_video_clips_name:
            if not (yandex_disk.exists(db_video_clip_path['path'])):
                mysqlfunc.del_video_clips_name(db_video_clip_path['path'])

def scheduled_task():
    try:
        current_time_utc = pytz.datetime.datetime.now(utc_tz)
        time_now=current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
        mysqlfunc.clean_render_hosts_status(time_now)
        print("Очистка списка онлайн рендер хостов выполнена")
        sync_yandex_clips_list()
        print("Загрузка в базу данных актуальных видео с яндекс диска")
    except Exception as e:
        print(f'Ошибка в задаче по расписанию {e}')
def online_host_clean_task():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    schedule.every(1).minutes.do(scheduled_task)
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    app.run(host="0.0.0.0",debug=False)