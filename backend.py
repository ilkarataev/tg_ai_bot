import io,requests,time
from libs import config as configs
from libs import mysql as mysqlfunc
from flask import Flask, request, jsonify, send_file
import threading
import schedule
app = Flask(__name__)

data_list = []
rest_api_url='/tg-ai-bot/rest/v1/'

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
    
@app.route(f'{rest_api_url}set_rendering_duration', methods=['POST'])
def set_rendering_duration():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        render_time = data['render_time']

        response = mysqlfunc.update_render_time(tg_user_id, render_time)
        return response

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
        if (tg_user_id != ''):
            response_image=mysqlfunc.get_photo_to_render(tg_user_id)
            blob_file = io.BytesIO(response_image)
            return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name=str(tg_user_id)+'_photo')

@app.route(f'{rest_api_url}get_client', methods=['GET'])
def get_client():
    print(request.method)
    if request.method == 'GET':
        with open('client.py', 'rb') as file:
            client_code = file.read()
        blob_file = io.BytesIO(client_code)
        return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name='client.py')

@app.route(f'{rest_api_url}set_status', methods=['POST'])
def set_status():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        status = data['status']
        if (tg_user_id != '' and status !=''):
            response=mysqlfunc.set_status(tg_user_id,status)
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
            print(r)
            return "True"

@app.route(f'{rest_api_url}send_video', methods=['POST'])
def send_video_file():
    final_message = """
    📱 Важное уведомление для пользователей iPhone! 📱

    Если вы пользуетесь iPhone и столкнулись с проблемами в пропорциях видео, мы рекомендуем вам

    Скачайте видеоролик на ваше устройство.
    После скачивания пропорции видео должны стать нормальными.

    Спасибо, что выбираете наш сервис!
    Для остановки бота нажмите /stop.
    Для повторного запуска /start
    """
    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
        "content-type": "application/json"
    }
    if request.method == 'POST':
        chat_id=request.form.get('chat_id')
        video_file = request.files['file']
        video_data = {
            'video': (video_file.filename, video_file, 'video/mp4')
        }

        url = f'https://api.telegram.org/bot{configs.bot_token}/sendVideo'
        data = {'chat_id': chat_id}
        r = requests.post(url, data=data, files=video_data)
        if (r.status_code == 200):
            url = f'https://api.telegram.org/bot{configs.bot_token}/sendMessage'
            data = {'chat_id': chat_id,'text':final_message}
            r = requests.post(url, json=data,headers=headers)
            return "True"
        else:
            print("Проблемы с отправкой файла в телеграмм")
            return "False"
    else:
        print("Проблемы с получением ключа бота")
        return
@app.route(f'{rest_api_url}set_render_host_status', methods=['POST'])
def set_render_host_status():
    if request.method == 'POST':
        data = request.json
        render_host_hostname = data['render_host_hostname']
        status = data['status']
        if (render_host_hostname != '' and status !='' ):
            record_date=time.strftime('%Y-%m-%d %H:%M:%S')
            mysqlfunc.set_render_host_status(render_host_hostname,status,record_date)
            return "True"
def scheduled_task():
    time_now=time.strftime('%Y-%m-%d %H:%M:%S')
    mysqlfunc.clean_render_hosts_status(time_now)
    print("Очистка списка онлайн рендер хостов выполнена")

def online_host_clean_task():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    schedule.every(5).minutes.do(scheduled_task)
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    #run backend
    app.run(host="0.0.0.0",debug=False)