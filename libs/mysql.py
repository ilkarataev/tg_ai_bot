# from msilib.schema import Error
import pymysql,sys
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
        print(f'В функции mysql insert_log что-то пошло не так: {e}')

def insert_user_data(name, surname, tg_user_id, clip_name):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `users` (`name`, `surname`, `tg_user_id`, `clip_name`) \
                VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, surname, tg_user_id, clip_name))
    except Exception as e:
        print(f'В функции mysql insert_user_data что-то пошло не так: {e}')
def clean_unfinish(tg_user_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "DELETE FROM `users` WHERE `tg_user_id`= %s AND `photo`IS NULL"
                cursor.execute(sql, (tg_user_id))
    except Exception as e:
        print(f'В функции mysql clean_unfinish что-то пошло не так: {e}')

def update_user_data(downloaded_photo, tg_user_id, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) as cnt FROM `users` WHERE `tg_user_id`= %s"
                cursor.execute(sql, (tg_user_id))
                result=cursor.fetchone()
                render_counter=result['cnt']+1
                sql = "UPDATE `users` SET `photo`=%s, `record_date`=%s, `render_counter`=%s WHERE `tg_user_id`= %s AND `photo` IS NULL"
                cursor.execute(sql, (downloaded_photo, record_date, render_counter, tg_user_id))
    except Exception as e:
        print(f'В функции mysql update_user_data что-то пошло не так: {e}')

def insert_tg_users(name, surname, tg_user_id, username, language_code, reg_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT `tg_user_id` FROM `tg_users` WHERE `tg_user_id` = %s"
                cursor.execute(sql, (tg_user_id,))
                result = cursor.fetchone()
                if result is None:
                    sql = "INSERT INTO `tg_users` (`name`, `surname`, `tg_user_id`, `username`, `language_code`, `reg_date`) \
                    VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (name, surname, tg_user_id, username, language_code, reg_date))
    except Exception as e:
        print(f'В функции mysql insert_tg_users что-то пошло не так: {e}')

def insert_bot_step(tg_user_id, bot_step, step_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `tg_bot` (`tg_user_id`, `bot_step`, `step_date`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (tg_user_id, bot_step, step_date))
    except Exception as e:
        print(f'В функции mysql bot_step что-то пошло не так: {e}')

def get_bot_step(tg_user_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT *  FROM `tg_bot` WHERE `tg_user_id`=%s  ORDER BY id DESC, step_date DESC"
                cursor.execute(sql, (tg_user_id))
                result=cursor.fetchone()
                if result == None:
                    return ''
                return result['bot_step']
    except Exception as e:
        print(f'В функции mysql get_bot_step что-то пошло не так: {e}')

def get_language_code(tg_user_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT *  FROM `tg_users` WHERE `tg_user_id`=%s"
                cursor.execute(sql, (tg_user_id))
                result=cursor.fetchone()
                if result == None:
                    return 'ru'
                return result['language_code']
    except Exception as e:
        print(f'В функции mysql get_language_code что-то пошло не так: {e}')

def check_user_render_queue(tg_user_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT status FROM `users` WHERE  `tg_user_id`=%s ORDER BY `record_date` DESC LIMIT 1"
                cursor.execute(sql, (tg_user_id))
                result=cursor.fetchone()
                if result == None or result['status'] == 'complete' or result['status'].lower()  == 'error' or result['status'] == 'rendring_error':
                    return True
                else:
                    return False
    except Exception as e:
        print(f'В функции mysql check_user_render_queue что-то пошло не так: {e}')

def get_task_to_render():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT tg_user_id,clip_name,DATE_FORMAT(record_date, '%Y-%m-%d %H:%i:%s') as record_date FROM `users` WHERE status='ready_to_render' ORDER BY record_date LIMIT 1"
                cursor.execute(sql)
                return cursor.fetchone()
    except Exception as e:
        print(f'В функции mysql get_task_to_render что-то пошло не так: {e}')

def set_video_clips(name_en,name_ru,url,path,md5,category):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `video_clips` (name_en, name_ru, url, path, md5, category) \
                VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name_en = VALUES(name_en), name_ru = VALUES(name_ru), url = VALUES(url), \
                path = VALUES(path), md5 = VALUES(md5), category = VALUES(category);"
                cursor.execute(sql,(name_en,name_ru,url,path,md5,category))
                return True
    except Exception as e:
        print(f'В функции mysql set_video_clips что-то пошло не так: {e}')

def get_video_clips_name(request='', category='', name_en=''):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if request == 'path':
                    sql = "SELECT path FROM `video_clips`"
                elif request == 'url':
                    sql = "SELECT url FROM `video_clips` WHERE name_en=%s"
                    cursor.execute(sql,name_en)
                    video_clip_url=cursor.fetchall()
                    return video_clip_url
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
        print(f'В функции mysql get_video_clips_name что-то пошло не так: {e}')

def del_video_clips_name(path):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "DELETE FROM `video_clips` WHERE path= %s"
                cursor.execute(sql,path)
                return True
    except Exception as e:
        print(f'В функции mysql del_video_clips_name что-то пошло не так: {e}')

def get_photo_to_render(tg_user_id,record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if record_date == 'check':
                    sql = "SELECT photo FROM `users` WHERE tg_user_id=%s ORDER BY record_date DESC LIMIT 1"
                    cursor.execute(sql,(tg_user_id))
                    photo_data=cursor.fetchone()
                    if photo_data == None: return False
                else:
                    sql = "SELECT photo FROM `users` WHERE tg_user_id=%s AND record_date=%s LIMIT 1"
                    cursor.execute(sql,(tg_user_id,record_date))
                    photo_data=cursor.fetchone()
                return photo_data['photo']
    except Exception as e:
        print(f'В функции mysql get_photo_to_render что-то пошло не так: {e}')

def update_render_time(tg_user_id, render_time, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET render_time=%s WHERE tg_user_id=%s and record_date=%s"
                cursor.execute(sql, (render_time, tg_user_id, record_date))
                return 'Время рендеринга обновлено успешно'
    except Exception as e:
        print(f'В функции mysql update_render_time что-то пошло не так: {e}')

def update_render_host(tg_user_id, render_host):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET render_host=%s WHERE tg_user_id=%s"
                cursor.execute(sql, (render_host, tg_user_id))
                connection.commit()  # Don't forget to commit the changes
                return 'Render host updated successfully'
    except Exception as e:
        print(f'В функции mysql update_render_host что-то пошло не так: {e}')

def check_record_exists(tg_user_id, record_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE tg_user_id = %s AND record_date = %s"
                cursor.execute(sql, (tg_user_id, record_date))
                result = cursor.fetchone()
                return bool(result)
    except Exception as e:
        print(f'В функции mysql check_record_exists что-то пошло не так: {e}')



#вроед не используется очистить
# def set_status_sent_to_user(tg_user_id):
#     try:
#          with getConnection() as connection:
    #         with connection.cursor() as cursor:
    #             sql = "UPDATE `users` SET status='sent_to_user' WHERE tg_user_id=%s"
    #             cursor.execute(sql, (tg_user_id,))
    #             return 'Status updated to sent_to_user'
#     except Exception as e:
#         print('В функции mysql set_status_sent_to_user что-то пошло не так: {e}')
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
        print(f'В функции mysql set_status что-то пошло не так: {e}')

def set_render_host_status(render_host_hostname,status,record_date):
    #  online
    #  offline
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                result_render_enabled=render_host_enabled(render_host_hostname)
                sql = " INSERT INTO `render_hosts` (`render_host`, `network_status`, `record_date`,`render_enabled`) \
                        VALUES (%s, %s, %s, %s) \
                        ON DUPLICATE KEY UPDATE \
                        `network_status` = VALUES(`network_status`), \
                        `record_date` = VALUES(`record_date`);"

                cursor.execute(sql, (render_host_hostname, status,record_date,result_render_enabled))
                return 'Status updated sucessful'
    except Exception as e:
        print(f'В функции mysql set_render_host_status что-то пошло не так: {e}')

def render_host_enabled(render_host_hostname):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT render_enabled FROM `render_hosts` WHERE render_host=%s;"
                cursor.execute(sql, str(render_host_hostname))
                result=cursor.fetchone()
                if result and result['render_enabled'] is not None:
                    render_enabled = result['render_enabled']
                else:
                    render_enabled = 1
                return render_enabled
    except Exception as e:
        print(f'В функции mysql render_host_enabled что-то пошло не так: {e}')

def clean_render_hosts_status(time_now):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `render_hosts` SET `network_status`='offline' WHERE `record_date` <= %s - INTERVAL 5 MINUTE;"
                cursor.execute(sql, (time_now))
    except Exception as e:
        print(f'В функции mysql clean_render_hosts_status что-то пошло не так:{e}')

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
        print(f'В функции mysql set_payment что-то пошло не так: {e}')

def insert_final_clip_size(tg_user_id, record_date, file_size_megabytes):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE `users` SET `final_clip_size`=%s WHERE `record_date`=%s AND `tg_user_id`=%s;"
                cursor.execute(sql, (int(file_size_megabytes), record_date, tg_user_id))
    except Exception as e:
        print(f'В функции mysql insert_final_clip_size что-то пошло не так:{e}')

# def insert_payment(tg_user_id,payment,summ,record_date):
#     try:
#         with getConnection() as connection:
#             with connection.cursor() as cursor:
#                 now_date = time.strftime('%Y-%m-%d %H:%M:%S')
#                 sql = INSERT INTO `payments` (`tg_user_id`, `render_enabled`, `payments_date`, `record_date`) \
#                         VALUES (%s, %s, %s, %s)"
#                 cursor.execute(sql,(tg_user_id, payment, record_date))
#     except:
#         print(f'В функции mysql insert_payment что-то пошло не так.')

def get_users_notification(language_code):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                if language_code == 'en':
                    sql = "SELECT `tg_user_id`,`language_code` FROM `tg_users` WHERE `language_code`is NULL OR `language_code`<>'ru';"
                    cursor.execute(sql)
                    result=cursor.fetchall()
                else:
                    sql = "SELECT tg_user_id FROM `tg_users` WHERE `language_code`=%s;"
                    cursor.execute(sql, str(language_code))
                    result=cursor.fetchall()
                return result
    except Exception as e:
        print(f'В функции mysql get_users_notification что-то пошло не так: {e}')

def get_notfication():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM bot_notification WHERE status is NULL LIMIT 1"
                cursor.execute(sql)
                result=cursor.fetchone()
                return result
    except Exception as e:
        print(f'В функции mysql get_notfication что-то пошло не так:{e}')

def set_notification(id, send_time, sended_count_summ):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE bot_notification SET `status`=%s, `send_date`=%s, `count_summ`=%s WHERE id=%s"
                cursor.execute(sql,('complete', send_time, sended_count_summ, id))

    except Exception as e:
        print(f'В функции mysql set_notification что-то пошло не так:{e}')