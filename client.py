import os.path,time,subprocess,shutil,tempfile,sys,socket,traceback,requests,filecmp
from datetime import datetime, date

# BASE_URL = 'http://127.0.0.1:5000/tg-ai-bot/rest/v1'
BASE_URL = 'https://ilkarvet.ru/tg-ai-bot/rest/v1'
media_path = os.path.join(os.getcwd(), 'media')  # Define media_path globally

def get_task():
    url = f'{BASE_URL}/get_task_to_render'
    response = requests.get(url)
    if response.status_code == 200:
        task = response.json()
        return task
    else:
        print(f'Запрос задания не выполнился, ошибка: {response.status_code}')
        return None

def get_photo(tg_user_id,input_face_file):
    url = f'{BASE_URL}/get_photo_to_render'
    data = {"tg_user_id": int(tg_user_id)}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(input_face_file, 'wb') as f:
            f.write(response.content)
        # Check if the input_face.png file exists
        if os.path.exists(input_face_file):
            print(f'Фото для видео успешно сохранено {input_face_file}')
        else:
            print(f'Файл с лицом не существует {input_face_file}')
            sys.exit(1)
    else:
        print(f'Файл(фото) для рендринга не найден,серверная ошибка: {response.status_code}')



def rendering(tg_user_id, clip_name, input_face_file, render_host):
    media_path=os.path.join(os.getcwd(), 'media')
    # Check if the Roop folder exists
    roop_path = os.path.join(os.getcwd(), 'Roop')
    if not os.path.exists(roop_path):
        print(f"Roop папки не существует по пути: {roop_path}")
        sys.exit()
    
    # Copy run_cli.py to the Roop folder
    run_cli_source = os.path.join(os.getcwd(), 'libs', 'run_cli.py')
    run_cli_destination = os.path.join(roop_path, 'run_cli.py')
    core_source = os.path.join(os.getcwd(), 'libs', 'core.py')
    core_destination = os.path.join(roop_path, 'roop', 'core.py')
    if not filecmp.cmp(run_cli_source, run_cli_destination):
        shutil.copy(run_cli_source, run_cli_destination)
    if not filecmp.cmp(core_source, core_destination):
        shutil.copy(core_source, core_destination)
    url = f'{BASE_URL}/update_render_host'
    data = {'tg_user_id': tg_user_id, 'render_host': render_host}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        print(f"Обновлен хост для задачи пользователя {tg_user_id}")
    else:
        print("Не удалось обновить статус задачи, работа скрипта завершается")
        sys.exit(1)
    # Переменные среды необходимы для рендринга
    os.environ['appdata'] = 'tmp'
    os.environ['userprofile'] = 'tmp'
    os.environ['temp'] = 'tmp'
    os.environ['path'] = 'git\cmd;python;venv\scripts;ffmpeg'
    os.environ['cuda_path'] = 'venv\\Lib\\site-packages\\torch\\lib'
    
    render_output_file=os.path.join(media_path, 'output.mp4')

    render_original_video = os.path.join(media_path, f'{clip_name}.mp4')

    if os.path.basename(render_original_video) == clip_name + '.mp4':
        print("Start rendering")
        if render_host == 'karvet-Latitude-7420':
            subprocess_folder=os.path.join(os.getcwd(),'Roop')
            # set_status(tg_user_id,'rendring')
            start_time = time.time()  # Запускаем секундомер перед началом рендеринга
            render_command = [
            f'{subprocess_folder}/run.py',
            '--execution-provider', 'openvino',
            '--source', input_face_file,
            '--target',  render_original_video,
            '--output', render_output_file,
            '--many-faces',
            '--keep-fps'
            ]
        else:
            set_status(tg_user_id,'rendring')
            subprocess_folder=os.path.join(os.getcwd(),'Roop\\')
            start_time = time.time()  # Запускаем секундомер перед началом рендеринга
            render_command = [
            'Roop\\python\\python.exe',
            'run.py',
            '--execution-provider', 'cuda',
            '--source', input_face_file,
            '--target',  render_original_video,
            '--output', render_output_file,
            '--many-faces',
            '--keep-fps'
            ]
        if render_host != 'karvet-Latitude-74201':
            try:
                render_process = subprocess.Popen(render_command, cwd=subprocess_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = render_process.communicate()
                render_process.wait()  # Wait for the subprocess to finish
                render_process.terminate() # удаляем процесс питона для освобождения ресурсов
                if render_process.returncode != 0:
                    print("Произошла ошибка в процессе рендринга.")
                    print("Код возврата:", render_process.returncode)
                    if stdout:
                        error_message = stdout.decode("utf-8")
                        print(error_message)
                        if 'No face in source path detected'in error_message:
                            # set_status(tg_user_id,'error')
                            send_message(tg_user_id,'Нам не удалось распознать Лицо на фото, \
                                Просим вас перезапустить бота с другой фотографией. \
                                Для остановки бота нажмите /stop.\nДля повторного запуска /start.')

            except Exception as e:
                print(f"Error while rendering: {e}")
                sys.exit(1)
        if render_host == 'karvet-Latitude-7420':
            time.sleep(5)
        ###############################################
        # Proceed with rendering only if the render_original_video matches the clip_name
        # render_process=subprocess.run(['Roop\\python\\python.exe', 'run.py', '--execution-provider', 'cuda', '--source', input_face_file, '--target',  render_original_video, '--output', f'{media_path}\\output.mp4', '--keep-fps'],cwd=subprocess_folder)
        end_time = time.time()  # Останавливаем секундомер после завершения рендеринга
        render_time = int(end_time - start_time)  # Вычисляем время рендеринга в секундах
        if os.path.exists(render_output_file) and os.path.getsize(render_output_file) > 10e6:
            url = f'{BASE_URL}/set_rendering_duration'
            data = {'tg_user_id': tg_user_id, 'render_time': render_time}
            requests.post(url, json=data)
            if send_video_file(tg_user_id,render_output_file):
                if render_host != 'karvet-Latitude-7420':
                    set_status(tg_user_id,'complete')
                    delete_files(input_face_file,render_output_file)
        else:
            print('Файл финального рендринга не существует проверьте скрипт')
            sys.exit(1)

    else:
        print("В папке media не содержится исхдного видео")
        sys.exit(1)
        
def set_status(tg_user_id,status):
    # Retrieve the necessary information (clip_name and render_host)
    url = f'{BASE_URL}/set_status'
    data = {'tg_user_id': tg_user_id, 'status': status}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        print("Статус задачи обновлен")
    else:
        print("Статус задачи не обновлен проблемы на сервере")

def send_message(chat_id,message):
    url = f'{BASE_URL}/send_message'
    headers = {'Content-Type': 'application/json'}
    data = {"chat_id": chat_id,"message": message}
    r = requests.post(url, json=data,headers=headers)
    if (r.status_code == 200):
        print(f"Сообщение {message} отправлен пользователю")
        return True

def send_video_file(chat_id, render_output_file):
#     #переделать на отправку с бека
    video_file = {'file': open(render_output_file, 'rb')}
    url = f'{BASE_URL}/send_video'
    data = {'chat_id': chat_id}
    r = requests.post(url, data=data, files=video_file)
    if (r.status_code == 200):
        print("Видео файл отправлен пользователю")
        return True
    else:
        print("Проблемы с отправкой файла пользователю")
        sys.exit(1)

def delete_files(input_face_file,render_output_file):
    try:
        os.remove(input_face_file)
        os.remove(render_output_file)
        print(f'Файлы удалены {input_face_file}, {render_output_file}')
    except OSError as e:
        print(f'Возникла проблема при удалении файлов {e}')
        sys.exit(1)

def set_render_host_status(render_host):
    url = f'{BASE_URL}/set_render_host_status'
    data = {'render_host_hostname': render_host, 'status': 'online'}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        print("Статус хоста обновлен")
    else:
        print(f"Статус хоста не обновлен проблемы на сервере {r.status_code}")

def git_pull_rebase():
    try:
        subprocess.run(['git', 'pull', '--rebase'], check=True)
        print("Выполнено обновление Git с перебазированием успешно")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении обновления Git с перебазированием: {e}")
        sys.exit(1)

if __name__ == '__main__':
    while True:
        try:
            timeout=50
            input_face_file = os.path.join(tempfile.gettempdir(), 'input_face.png')
            render_host = socket.gethostname()  # Берем имя машины
            set_render_host_status(render_host)
            response = get_task()
            if response:
                tg_user_id = response['tg_user_id']
                clip_name = response['clip_name']
                get_photo(tg_user_id,input_face_file)
                try:
                    rendering(tg_user_id, clip_name, input_face_file, render_host)
                    print(f"Задача на рендер выполнена таймаут {timeout} секунд")
                except:
                    # git_pull_rebase()
                    raise  # Пробросить исключение дальше
            else:
                print(f"Задачи на рендер не найдены таймаут {timeout} секунд")
                # git_pull_rebase()  # Выполнить обновление Git с перебазированием
            time.sleep(timeout)
        except Exception as e:
            print(e)
            trace = traceback.print_exc()
            print(traceback.format_exc())
            print(f'{e} --------- {trace}')
        time.sleep(timeout)
            
 
