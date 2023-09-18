# from msilib.schema import Error
import pymysql,time
import pymysql.cursors
from libs import config as configs
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
        # print("MySQL Connection Sucessfull!")
        return connection
    except Exception as err:
        print(f"MySQL Connection Failed !{err}")
        sys.exit(1)

def insert_log(log):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `logs` (`log`) VALUES (%s)"
                cursor.execute(sql, log)
    except Exception as e:
        print(f'В функции insert_log что-то пошло не так: {e}')

def insert_user_data(name,surname,downloaded_photo,tg_user_id, clip_name, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) as cnt FROM `users` WHERE `tg_user_id`= %s"
                cursor.execute(sql, (tg_user_id))
                result=cursor.fetchone()
                render_counter=result['cnt']+1
                sql = "INSERT INTO `users` (`Name`,`Surname`, `photo`, `tg_user_id`, `clip_name`, `record_date`, render_counter) \
                VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (name,surname,downloaded_photo,tg_user_id, clip_name, record_date,render_counter))
    except Exception as e:
        print(f'В функции insert_user_data что-то пошло не так: {e}')

def insert_photos(photo, tg_user_id, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `photos` (`tg_user_id`,  `photo`, `record_date` ) VALUES (%s, %s, %s)"
                cursor.execute(sql, (tg_user_id, photo, record_date))
    except Exception as e:
        print(f'В функции insert_photos что-то пошло не так: {e}')

def get_task_to_render():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT tg_user_id,clip_name,DATE_FORMAT(record_date, '%Y-%m-%d %H:%i:%s') as record_date FROM `users` WHERE status='ready_to_render' ORDER BY record_date LIMIT 1"
                cursor.execute(sql)
                # print(cursor.fetchone())
                return cursor.fetchone()
    except Exception as e:
        print(f'В функции get_task_to_render что-то пошло не так: {e}')

def set_video_clips(name_en,name_ru,url,path,md5,category):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `video_clips` (name_en, name_ru, url, path, md5, category) \
                VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name_en = VALUES(name_en), name_ru = VALUES(name_ru), url = VALUES(url), \
                path = VALUES(path), md5 = VALUES(md5), category = VALUES(category);"
                # sql = "INSERT IGNORE INTO `video_clips` (name_en, name_ru, hash_url) VALUES (%s,%s,%s);"
                cursor.execute(sql,(name_en,name_ru,url,path,md5,category))
                return True
    except Exception as e:
        print(f'В функции set_video_clips что-то пошло не так: {e}')

def get_video_clips_name(request='',category=''):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if request == 'path':
                    sql = "SELECT path FROM `video_clips`"
                elif request == 'category':
                    sql = "SELECT DISTINCT (category) FROM video_clips;"
                elif request == 'by_category':
                    sql = f"SELECT * FROM `video_clips` WHERE `category`= '{category}'"
                else:
                    sql = "SELECT * FROM `video_clips`"
                cursor.execute(sql)
                video_clips=cursor.fetchall()
                return video_clips
    except Exception as e:
        print(f'В функции get_video_clips_name что-то пошло не так: {e}')

def del_video_clips_name(path):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "DELETE FROM `video_clips` WHERE path= %s"
                cursor.execute(sql,path)
                return True
    except Exception as e:
        print(f'В функции del_video_clips_name что-то пошло не так: {e}')

def get_photo_to_render(tg_user_id,record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if record_date == 'check':
                    sql = "SELECT photo FROM `photos` WHERE tg_user_id=%s ORDER BY record_date DESC LIMIT 1"
                    cursor.execute(sql,(tg_user_id))
                    photo_data=cursor.fetchone()
                    if photo_data == None: return False
                else:
                    sql = "SELECT photo FROM `photos` WHERE tg_user_id=%s AND record_date=%s LIMIT 1"
                    cursor.execute(sql,(tg_user_id,record_date))
                    photo_data=cursor.fetchone()
                return photo_data['photo']
    except Exception as e:
        print(f'В функции get_photo_to_render что-то пошло не так: {e}')

def update_render_time(tg_user_id, render_time, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET render_time=%s WHERE tg_user_id=%s and record_date=%s"
                cursor.execute(sql, (render_time, tg_user_id, record_date))
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

def set_status(tg_user_id,status,record_date):
    #  ready_to_render
    #  rendring
    #  render_complete
    #  error
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET status=%s WHERE tg_user_id=%s AND record_date=%s"
                cursor.execute(sql,(status, tg_user_id, record_date))
                return 'Status updated sucessful'
    except Exception as e:
        print(f'В функции set_status что-то пошло не так: {e}')

def set_render_host_status(render_host_hostname,status,record_date):
    #  online
    #  offline
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                result_render_enabled=render_host_enabled(render_host_hostname)
                logger.info(result_render_enabled)
                # sys.exit()
                sql = " INSERT INTO `render_hosts` (`render_host`, `network_status`, `record_date`,`render_enabled`) \
                        VALUES (%s, %s, %s, %s) \
                        ON DUPLICATE KEY UPDATE \
                        `network_status` = VALUES(`network_status`), \
                        `record_date` = VALUES(`record_date`);"

                cursor.execute(sql, (render_host_hostname, status,record_date,result_render_enabled))
                return 'Status updated sucessful'
    except Exception as e:
        print(f'В функции set_render_host_status что-то пошло не так: {e}')

def render_host_enabled(render_host_hostname):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT render_enabled FROM `render_hosts` WHERE render_host=%s;"
                cursor.execute(sql, str(render_host_hostname))
                result=cursor.fetchone()
                # logger.info('result')
                # print(bool(result['render_enabled']))
                # return  True
                return str(result['render_enabled'])
    except Exception as e:
        print(f'В функции render_host_enabled что-то пошло не так: {e}')

def clean_render_hosts_status(time_now):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `render_hosts` SET `network_status`='offline' WHERE `record_date` <= %s - INTERVAL 5 MINUTE;"
                cursor.execute(sql, (time_now))
    except Exception as e:
        print(f'В функции clean_render_hosts_status что-то пошло не так:{e}')

def set_payment(tg_user_id,record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                result_render_enabled=render_host_enabled(render_host_hostname)
                sql = " INSERT INTO `payments` \
                    (`tg_user_id`, `payments_date`) VALUES (%s, %s)"

                cursor.execute(sql, (tg_user_id, record_date))
                return 'Payments updated sucessful'
    except Exception as e:
        print(f'В функции set_payment что-то пошло не так: {e}')

# def insert_payment(tg_user_id,payment,summ,record_date):
#     try:
#         with getConnection() as connection:
#             with connection.cursor() as cursor:
#                 now_date = time.strftime('%Y-%m-%d %H:%M:%S')
#                 sql = INSERT INTO `payments` (`tg_user_id`, `render_enabled`, `payments_date`, `record_date`) \
#                         VALUES (%s, %s, %s, %s)"
#                 cursor.execute(sql,(tg_user_id, payment, record_date))
#     except:
#         print(f'В функции insert_payment что-то пошло не так.')

