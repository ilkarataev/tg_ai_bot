import os.path,time,subprocess,shutil,tempfile
import sys,socket,traceback,requests,filecmp,psutil,os
import logging, logging.handlers
from datetime import datetime, date
import argparse,hashlib
from urllib.parse import urlparse

BASE_URL_LOCAL = 'http://127.0.0.1:5000/tg-ai-bot/rest/v1'
BASE_URL_PROD = 'https://ilkarvet.ru/tg-ai-bot/rest/v1'

media_path = os.path.join(os.getcwd(), 'media')  # Define media_path globally

class HostnameFilter(logging.Filter):
    hostname = socket.gethostname()
    def filter(self, record):
        record.hostname = self.hostname
        return True

def create_logger(base_url):
    parsed_url = urlparse(base_url)
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 5000)
    # Создание HTTPHandler с распарсенным хостом и путем
    http_handler = logging.handlers.HTTPHandler(
        f"{parsed_url.hostname}:{port}",
        parsed_url.path + "/logs",
        method='POST'
    )
    formatter = logging.Formatter('%(hostname)s - %(levelname)s - %(message)s')
    http_handler.setFormatter(formatter)
    http_handler.setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.addHandler(http_handler)
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addFilter(HostnameFilter())
    logger.setLevel(logging.DEBUG)
    return logger

def check_url():
    url = f'{BASE_URL_LOCAL}/ready'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BASE_URL_LOCAL
    except:
        return BASE_URL_PROD

def get_task():
    url = f'{BASE_URL}/get_task_to_render'
    response = requests.get(url)
    if response.status_code == 200:
        task = response.json()
        return task
    else:
        logger.error(f'Запрос на получение задания не выполнился, ошибка: {response.status_code}')
        return None

def get_photo(tg_user_id,input_face_file,record_date):
    url = f'{BASE_URL}/get_photo_to_render'
    data = {"tg_user_id": int(tg_user_id),"record_date":record_date}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(input_face_file, 'wb') as f:
            f.write(response.content)
        if os.path.exists(input_face_file):
            logger.info(f'Фото для видео успешно сохранено {input_face_file}')
        else:
            logger.error(f'Файл с лицом не существует {input_face_file}')
            sys.exit(1)
    else:
        logger.error(f'Файл(фото) для рендринга не найден,серверная ошибка: {response.status_code}')

def download_and_update_video(video_url, local_clip_file):
    try:
        r = requests.get(video_url)
        if (r.status_code == 200):
            with open(local_clip_file, "wb") as f:
                f.write(r.content)
            logger.info(f"Файл загружен из яндекса {local_clip_file}")
        elif (r.status_code !=200):
            logger.error(f"Файл не загружен из яндекса {local_clip_file}. HTTP ошибка {r.status_code}")
    except requests.exceptions.RequestException:
        logger.error(f"Проблемы с загрузкой файла {local_clip_file}")

def download_clip_file(media_path,clip_name):
    try:
        api_url = f'{BASE_URL}/get_video_clips'
        r = requests.get(api_url)
        if (r.status_code == 200):
            video_clips = r.json()
        elif(r.status_code !=200):
            logger.error(f"Не удалось получить информацию о следующем видеоролике для рендеринга {clip_name}.")
            logger.error(f"{BASE_URL}  route get_video_clips")
            return
        for clip in video_clips:
            if clip_name == clip['name_en']:
                remote_video_url = clip['url']
                remote_md5 = clip['md5']
                if os.path.exists(media_path):
                    local_clip_file=os.path.join(media_path, f'{clip_name}.mp4')
                    if os.path.exists(local_clip_file):
                        with open(local_clip_file, "rb") as f:
                            current_client=f.read()
                        local_clip_file_md5 = calculate_md5(current_client)
                        if local_clip_file_md5 != remote_md5:
                            logger.info(f"Локальное видео {clip['name_en']} устарело. Загрузка новой версии.")
                            download_and_update_video(remote_video_url, local_clip_file)
                            time.sleep(5) #баги при ренедере когда скачался файл.
                        else:
                            logger.info(f"Локальное видео {clip['name_en']} актуально. Готово для рендеринга.")
                    else:
                        logger.info(f"Локальное видео {clip['name_en']} не существует. Загрузка впервые.")
                        download_and_update_video(remote_video_url, local_clip_file)
                        time.sleep(5) #баги при ренедере когда скачался файл.
    except Exception as e:
        logger.error(f"Ошибка в функции загрузки файлов из яндекса {e}")

def rendering(tg_user_id, clip_name, record_date, input_face_file, render_host):
    media_path=os.path.join(os.getcwd(), 'media')
    os_system=''

    if not os.path.exists(media_path):
        os.makedirs(media_path)
        logger.info(f"Создана папка 'media' по пути: {media_path}")

    # Check if the Roop folder exists
    roop_path = os.path.join(os.getcwd(), 'Roop')
    if not os.path.exists(roop_path):
        logger.info(f"Roop папки не существует по пути: {roop_path}")
        logger.error(f"Для работы рендера необходим проект ROOP")
        sys.exit(1)
    
    # Copy run_cli.py to the Roop folder
    #Переделать на скачивания с сервера
    base_path = os.path.join(os.getcwd(), 'libs/for_roop/')
    files_to_copy = [
        (os.path.join(base_path, 'run_cli.py'), os.path.join(roop_path, 'run_cli.py')),
        (os.path.join(base_path, 'core.py'), os.path.join(roop_path, 'roop', 'core.py')),
        (os.path.join(base_path, 'face_swapper.py'), os.path.join(roop_path, 'roop/processors/frame/', 'face_swapper.py'))
    ]

    for source, destination in files_to_copy:
        if os.path.exists(source) or not filecmp.cmp(source, destination, shallow=False):
            shutil.copy(source, destination)
    url = f'{BASE_URL}/update_render_host'
    data = {'tg_user_id': tg_user_id, 'render_host': render_host}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        logger.info(f"Обновлен хост для задачи пользователя {tg_user_id}")
    elif (r.status_code !=200):
        logger.error(f"Не удалось обновить статус задачи для пользователя {tg_user_id}, работа скрипта завершается")
        sys.exit(1)
    # Переменные среды необходимы для рендринга
    os.environ['appdata'] = 'tmp'
    os.environ['userprofile'] = 'tmp'
    os.environ['temp'] = 'tmp'
    os.environ['path'] = 'git\cmd;python;venv\scripts;ffmpeg'
    os.environ['cuda_path'] = 'venv\\Lib\\site-packages\\torch\\lib'
    
    render_output_file=os.path.join(media_path, 'output.mp4')
    download_clip_file(media_path,clip_name)
    render_original_video = os.path.join(media_path, f'{clip_name}.mp4')

    if os.name == 'posix':
        os_system='Unix'
        logger.info('ОС определена Unix-like')
    elif os.name == 'nt':
        os_system='Windows'
        logger.info('ОС определена Windows')
    else:
        logger.info('Неизвестная OS скрипт работа скрипта завершается')
        sys.exit(1)
    
    if os.path.basename(render_original_video) == clip_name + '.mp4':
        logger.info((
            f"Запуск рендринга для пользователя {tg_user_id}.\n"
            f"Задача с временой отметкой {record_date},\n"
            f"Видео для рендера {clip_name}\n"
        ))
        if render_host == 'karvet-Latitude-7420':
            subprocess_folder=os.path.join(os.getcwd(),'Roop')
            set_status(tg_user_id,'rendring',record_date)
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
        elif os_system == 'Unix':
            subprocess_folder=os.path.join(os.getcwd(),'Roop')
            set_status(tg_user_id,'rendring',record_date)
            start_time = time.time()  # Запускаем секундомер перед началом рендеринга
            render_command = [
            f'{subprocess_folder}/run.py',
            '--execution-provider', 'cuda',
            '--source', input_face_file,
            '--target',  render_original_video,
            '--output', render_output_file,
            '--many-faces',
            '--keep-fps'
            ]
        elif os_system == 'Windows':
            set_status(tg_user_id,'rendring',record_date)
            subprocess_folder=os.path.join(os.getcwd(),'Roop\\')
            start_time = time.time()  # Запускаем секундомер перед началом рендеринга
            render_command = [
            'Roop\\python\\python.exe',
            'run_cli.py',
            '--execution-provider', 'cuda',
            '--max-memory', '2',
            '--execution-threads', '2',
            '--source', input_face_file,
            '--target',  render_original_video,
            '--output', render_output_file,
            '--many-faces',
            '--keep-fps'
            ]
        if render_host != 'karvet-Latitude-742110':
            try:
                render_process = subprocess.Popen(render_command, cwd=subprocess_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = render_process.communicate()
                render_process.wait()  # Wait for the subprocess to finish
                render_process.terminate() # удаляем процесс питона для освобождения ресурсов

                if render_process.returncode != 0:
                    logger.error("Произошла ошибка в процессе рендринга.")
                    logger.error("Код возврата:", render_process.returncode)
                    logger.error("Stderror-##############################")
                    logger.error(stderr)
                    logger.error("Stdout-################################")
                    logger.error(stdout)
                    if stdout:
                        error_message = stdout.decode("utf-8")
                        logger.error(error_message)
                        if 'No face in source path detected'in error_message:
                            logger.error('No face in source path detected')
                            set_status(tg_user_id,'error_no_face',record_date)
                            send_message(tg_user_id,'Нам не удалось распознать Лицо на фото, \
                                Просим вас перезапустить бота с другой фотографией. \
                                Для остановки бота нажмите /stop.\nДля повторного запуска /start.')

            except Exception as e:
                logger.error(f"Ошибка в процессе рендринга: {e}")
                set_status(tg_user_id,'rendring_error',record_date)
                sys.exit(1)
        if render_host == 'karvet-Latitude-7420':
            time.sleep(5)
        end_time = time.time()
        render_time = int(end_time - start_time)
        if os.path.exists(render_output_file) and os.path.getsize(render_output_file) >  100 * 1024:  # 100 KB:
            url = f'{BASE_URL}/set_rendering_duration'
            data = {'tg_user_id': tg_user_id, 'render_time': render_time, 'record_date': record_date}
            r=requests.post(url, json=data)
            if send_video_file(tg_user_id,render_output_file):
                set_status(tg_user_id,'complete',record_date)
                if render_host != 'karvet-Latitude-7420':
                    delete_files(input_face_file,render_output_file)
            else:
                set_status(tg_user_id,'error in func send_video_file ',record_date)
        else:
            set_status(tg_user_id,'error',record_date)
            logger.error('Файл финального рендринга не существует проверьте скрипт')
            sys.exit(1)

    else:
        logger.error("В папке media не содержится исходного файла для рендринга видео")
        sys.exit(1)
        
def set_status(tg_user_id,status,record_date):
    # Retrieve the necessary information (clip_name and render_host)
    url = f'{BASE_URL}/set_status'
    data = {'record_date':record_date,'tg_user_id': tg_user_id, 'status': status}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        logger.info("Статус задачи обновлен")
    elif (r.status_code !=200):
        logger.error("Статус задачи не обновлен проблемы на сервере")

def send_message(chat_id,message):
    url = f'{BASE_URL}/send_message'
    headers = {'Content-Type': 'application/json'}
    data = {"chat_id": chat_id,"message": message}
    r = requests.post(url, json=data,headers=headers)
    if (r.status_code == 200):
        logger.info(f"Сообщение {message} отправлен пользователю")
        return True
    elif (r.status_code !=200):
        logger.error(f"Сообщение {message} не удалось отправить пользователю {r.status_code }")

def send_video_file(chat_id, render_output_file):
    video_file = {'file': open(render_output_file, 'rb')}
    url = f'{BASE_URL}/send_video'
    data = {'chat_id': chat_id}
    r = requests.post(url, data=data, files=video_file)
    if (r.status_code == 200):
        logger.info("Видео файл отправлен пользователю")
        return True
    elif (r.status_code !=200):
        logger.error("Проблемы с отправкой файла пользователю")
        sys.exit(1)

def delete_files(input_face_file,render_output_file):
    try:
        os.remove(input_face_file)
        os.remove(render_output_file)
        logger.info(f'Файлы удалены {input_face_file}, {render_output_file}')
    except OSError as e:
        logger.error(f'Возникла проблема при удалении файлов {e}')
        sys.exit(1)

def set_render_host_status(render_host):
    url = f'{BASE_URL}/set_render_host_status'
    data = {'render_host_hostname': render_host, 'status': 'online'}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        logger.info("Статус хоста обновлен")
    else:
        logger.error(f"Статус хоста не обновлен проблемы на сервере {r.status_code}")

def render_host_enabled(render_host):
    url = f'{BASE_URL}/render_host_enabled'
    data = {'render_host_hostname': render_host}
    r = requests.post(url, json=data)
    if (r.status_code == 200):
        if (bool(int(r.content))):
            logger.info("Рендер для этого хоста включен")
            return True
    else:
        return False

def calculate_md5(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    md5_checksum = md5_hash.hexdigest()
    return md5_checksum

def get_client_code():
    parser = argparse.ArgumentParser(description="Пример скрипта с аргументами командной строки.")
    debug_response= {}
    # Добавляем аргументы
    parser.add_argument("--update", action="store_true", help="Обновление файла клиента")
    parser.add_argument("--debug", action="store_true", help="Запуск debug режима")
    args = parser.parse_args()

    if args.update:
        url = f'{BASE_URL}/get_client_code'
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open('client.py', "rb") as f:
                current_client=f.read()
            if calculate_md5(response.content) != calculate_md5(current_client):
                logger.info("Обновление локального клиента!")
                logger.info("MD5 клиента с сервера: " + calculate_md5(response.content))
                logger.info("MD5 клиента локальный: " + calculate_md5(current_client))
                with open('client.py', 'wb') as f:
                    f.write(response.content)
                sys.exit(0)
            elif calculate_md5(response.content) == calculate_md5(current_client):
                logger.info("Клиент не нуждается в обновлении")
                sys.exit(0)
    elif args.debug:
            debug_response['tg_user_id'] = '166889867'
            debug_response['clip_name'] = 'Matrix'
            debug_response['record_date'] = '2023-08-29 09:20:09'
            return debug_response

def kill_other_client_process(current_pid):
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            proc_info = proc.info
            pid = proc_info['pid']
            name = proc_info['name']
            create_time = proc_info['create_time']
            # Проверить, что это другой процесс client.py и не текущий процесс
            if  'python' in name and 'client.py' in psutil.Process(pid).cmdline() and pid != current_pid:
                now = time.time()
                elapsed_time = now - create_time
                if elapsed_time > 1500:  # 25 минут в секундах
                    p = psutil.Process(pid)
                    p.terminate()
                    logger.info(f"Процесс {pid} ({name}) завершен (работал больше 25 минут)")
                else:
                    logger.info(f"Процесс {pid} ({name}) работает меньше 25 минут, выходим с 0 статусом")
                    sys.exit(0)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == '__main__':
    current_pid = os.getpid()  # Получить PID текущего процесса (client.py)
    # Завершить другие экземпляры client.py перед выполнением
    kill_other_client_process(current_pid)
    # while True:
    try:
        timeout=6
        BASE_URL=check_url()
        logger=create_logger(BASE_URL)
        logger.info("Подключение к бэкенду по адресу: " + BASE_URL)
        debug_response=get_client_code()
        input_face_file = os.path.join(tempfile.gettempdir(), 'input_face.png')
        render_host = socket.gethostname()  # Берем имя машины
        set_render_host_status(render_host)
        #чтобы удаленно управлять клиентами
        if not render_host_enabled(render_host):
            logger.info(f"Рендер для этого Хоста: {render_host} отключен на сервере!!!!")
            sys.exit(0)
        if not debug_response:
            response = get_task()
        else:
            response=debug_response
        if response:
            tg_user_id = response['tg_user_id']
            clip_name = response['clip_name']
            record_date = response['record_date']

            get_photo(tg_user_id,input_face_file,record_date)
            
            try:
                rendering(tg_user_id, clip_name, record_date, input_face_file, render_host)
                logger.info(f"Задача на рендер выполнена таймаут {timeout} секунд")
            except Exception as e:
                logger.error(f'Ошибка в задаче рендринга {e}')
                raise
        else:
            logger.info(f"Задачи на рендер не найдены таймаут {timeout} секунд")
        time.sleep(timeout)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'{e}')
    time.sleep(timeout)
