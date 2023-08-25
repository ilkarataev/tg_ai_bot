# from msilib.schema import Error
import pymysql,time
import pymysql.cursors
from libs import config as configs
import hashlib
def getConnection():
    try:
        connection = pymysql.connect(host=configs.db_host,
                                    user=configs.db_user,
                                    password=configs.db_password,
                                    database=configs.db_name,
                                    port=int(configs.db_port),
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True);
        connection.ping(reconnect=True)
        print("MySQL Connection Sucessfull!")
        return connection
    except Exception as err:
        print(f"MySQL Connection Failed !{err}")
        sys.exit(1)
 
def insert_user_data(name,surname,tg_user_id, clip_name, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                # cursor.execute("DELETE FROM users WHERE tg_user_id=%s", (tg_user_id))
                sql = "INSERT INTO `users` (`Name`,`Surname`,`tg_user_id`, `clip_name`, `record_date`, `status`) VALUES (%s,%s,%s, %s, %s,'')"
                cursor.execute(sql, (name,surname,tg_user_id, clip_name, record_date))
    except Exception as e:
        print(f'В функции insert_user_data что-то пошло не так: {e}')

def insert_photos(photo, tg_user_id, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM photos WHERE tg_user_id=%s", (tg_user_id))
                sql = "INSERT INTO `photos` (`tg_user_id`,  `photo`, `record_date` ) VALUES (%s, %s, %s)"
                cursor.execute(sql, (tg_user_id, photo, record_date))
    except Exception as e:
        print(f'В функции insert_photos что-то пошло не так: {e}')

def get_status(tg_user_id, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT status FROM `users` WHERE `tg_user_id`= %s"
                cursor.execute(sql, (tg_user_id))
    except Exception as e:
        print(f'В функции get_status что-то пошло не так: {e}')

def get_task_to_render():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT tg_user_id,clip_name FROM `users` WHERE status='ready_to_render' ORDER BY record_date LIMIT 1"
                cursor.execute(sql)
                return cursor.fetchone()
    except Exception as e:
        print(f'В функции get_task_to_render что-то пошло не так: {e}')

def set_video_clips(name_en,name_ru,url):
    try:
        sha256_hash = hashlib.sha256()

        # Конвертируем URL в байты и обновляем хеш
        sha256_hash.update(url.encode('utf-8'))

        # Получаем шестнадцатеричное представление хеша
        hashed_url = sha256_hash.hexdigest()
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `video_clips` (name_en, name_ru, hash_url) \
                VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE name_en = VALUES(name_en), name_ru = VALUES(name_ru), hash_url = VALUES(hash_url);"
                # sql = "INSERT IGNORE INTO `video_clips` (name_en, name_ru, hash_url) VALUES (%s,%s,%s);"
                cursor.execute(sql,(name_en,name_ru,hashed_url))
                return True
    except Exception as e:
        print(f'В функции set_video_clips что-то пошло не так: {e}')

def get_video_clips_name(en=False):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if en:
                    sql = "SELECT name_en FROM `video_clips`"
                else:
                    sql = "SELECT * FROM `video_clips`"
                cursor.execute(sql)
                video_clips=cursor.fetchall()
                return video_clips
    except Exception as e:
        print(f'В функции get_video_clips_name что-то пошло не так: {e}')

def get_photo_to_render(tg_user_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT photo FROM `photos` WHERE tg_user_id=%s LIMIT 1"
                cursor.execute(sql,tg_user_id)
                photo_data=cursor.fetchone()
                return photo_data['photo']
    except Exception as e:
        print(f'В функции get_photo_to_render что-то пошло не так: {e}')

def update_render_time(tg_user_id, render_time):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET render_time=%s WHERE tg_user_id=%s"
                cursor.execute(sql, (render_time, tg_user_id))
                return 'Время рендеринга обновлено успешно'
    except Exception as e:
        print(f'В функции update_render_time что-то пошло не так: {e}')

def update_render_host(tg_user_id, render_host):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET render_host=%s WHERE tg_user_id=%s"
                cursor.execute(sql, (render_host, tg_user_id))
                connection.commit()  # Don't forget to commit the changes
                return 'Render host updated successfully'
    except Exception as e:
        print(f'В функции update_render_host что-то пошло не так: {e}')


#вроед не используется очистить
# def set_status_sent_to_user(tg_user_id):
#     try:
#          with getConnection() as connection:
    #         with connection.cursor() as cursor:
    #             sql = "UPDATE `users` SET status='sent_to_user' WHERE tg_user_id=%s"
    #             cursor.execute(sql, (tg_user_id,))
    #             return 'Status updated to sent_to_user'
#     except Exception as e:
#         print('В функции set_status_sent_to_user что-то пошло не так: {e}')
#     finally:
#         connection.close()

def set_status(tg_user_id,status):
    #  ready_to_render
    #  rendring
    #  render_complete
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET status=%s WHERE tg_user_id=%s"
                cursor.execute(sql, (status, tg_user_id))
                return 'Status updated sucessful'
    except Exception as e:
        print(f'В функции set_status что-то пошло не так: {e}')

def set_render_host_status(render_host_hostname,status,record_date):
    #  online
    #  offline
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = " INSERT INTO `render_hosts` (`render_host`, `network_status`, `record_date`) \
                        VALUES (%s, %s, %s) \
                        ON DUPLICATE KEY UPDATE \
                        `network_status` = VALUES(`network_status`), \
                        `record_date` = VALUES(`record_date`);"

                cursor.execute(sql, (render_host_hostname, status,record_date))
                return 'Status updated sucessful'
    except Exception as e:
        print(f'В функции set_render_host_status что-то пошло не так: {e}')

def clean_render_hosts_status(time_now):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `render_hosts` SET `network_status`='offline' WHERE `record_date` <= %s - INTERVAL 5 MINUTE;"
                cursor.execute(sql, (time_now))
    except Exception as e:
        print(f'В функции clean_render_hosts_status что-то пошло не так:{e}')

def payment_success(tg_user_id,dtp_date,record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                now_date = time.strftime('%Y-%m-%d %H:%M:%S')
                sql = "UPDATE `users` SET paid=1 WHERE tg_user_id=%s AND dtp_date=%s AND record_date=%s"
                cursor.execute(sql,(tg_user_id, dtp_date, record_date))
    except:
        print(f'В функции payment_success что-то пошло не так.')

