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
        print("MySQL Connection Sucessfull!")
        return connection
    except Exception as err:
        print("MySQL Connection Failed !")
        print(err)
        exit()
 
def insert_user_data(tg_user_id, clip_name, record_date, paid):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE tg_user_id=%s", (tg_user_id))
            sql = "INSERT INTO `users` (`tg_user_id`, `clip_name`, `record_date`, `paid`,`status`) VALUES (%s, %s, %s, %s,'')"
            cursor.execute(sql, (tg_user_id, clip_name, record_date, paid))
    except Exception as e:
        print('В функции insert_user_data что-то пошло не так:')
        print(e)
 
def insert_photos(photo, tg_user_id, record_date):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM photos WHERE tg_user_id=%s", (tg_user_id))
            sql = "INSERT INTO `photos` (`tg_user_id`,  `photo`, `record_date` ) VALUES (%s, %s, %s)"
            cursor.execute(sql, (tg_user_id, photo, record_date))
    except:
        print('В функции insert_photos что-то пошло не так.')

def get_status(tg_user_id, record_date):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "SELECT status FROM `users` WHERE `tg_user_id`= %s"
            cursor.execute(sql, (tg_user_id))
    except Exception as e:
        print('В функции get_status что-то пошло не так:')
        print(e)

def get_task_to_render():
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "SELECT tg_user_id,clip_name FROM `users` WHERE status='ready_to_render' ORDER BY record_date LIMIT 1"
            cursor.execute(sql)
            return cursor.fetchone()
    except Exception as e:
        print('В функции get_task что-то пошло не так:')
        print(e)

def get_video_clips_name():
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `video_clips`"
            cursor.execute(sql)
            video_clips=cursor.fetchall()
            return video_clips
    except Exception as e:
        print('В функции get_video_clips_name что-то пошло не так:')
        print(e)


def get_photo_to_render(tg_user_id):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "SELECT photo FROM `photos` WHERE tg_user_id=%s LIMIT 1"
            cursor.execute(sql,tg_user_id)
            photo_data=cursor.fetchone()
            return photo_data['photo']
    except Exception as e:
        print('В функции get_photo_to_render что-то пошло не так:')
        print(e)

def update_render_time(tg_user_id, render_time):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE `users` SET render_time=%s WHERE tg_user_id=%s"
            cursor.execute(sql, (render_time, tg_user_id))
            return 'Время рендеринга обновлено успешно'
    except Exception as e:
        print('Произошла ошибка в функции update_render_time:')
        print(e)

def update_render_host(tg_user_id, render_host):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE `users` SET render_host=%s WHERE tg_user_id=%s"
            cursor.execute(sql, (render_host, tg_user_id))
            connection.commit()  # Don't forget to commit the changes
            return 'Render host updated successfully'
    except Exception as e:
        print('An error occurred in the update_render_host function:')
        print(e)

def set_status_sent_to_user(tg_user_id):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE `users` SET status='sent_to_user' WHERE tg_user_id=%s"
            cursor.execute(sql, (tg_user_id,))
            return 'Status updated to sent_to_user'
    except Exception as e:
        print('An error occurred in the set_status_sent_to_user function:')
        print(e)


def set_status(tg_user_id,status):
    #  ready_to_render
    #  rendring
    #  render_complete
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE `users` SET status=%s WHERE tg_user_id=%s"
            cursor.execute(sql, (status, tg_user_id))
            return 'Status updated sucessful'
    except Exception as e:
        print('В функции set_status что-то пошло не так:')
        print(e)

def set_host_status(render_host_hostname,status):
    #  online
    #  offline
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO `render_hosts` (`render_host`,  `network_status`) VALUES (%s, %s)"
            cursor.execute(sql, (render_host_hostname, status))
            return 'Status updated sucessful'
    except Exception as e:
        print('В функции set_status что-то пошло не так:')
        print(e)

# def clean_hosts_status(render_host_hostname,status):
#     try:
#         connection = getConnection()
#         with connection.cursor() as cursor:
#             sql = "UPDATE `render_hosts` SET `network_status`='offline' WHERE recordtime<="
#             cursor.execute(sql, (render_host_hostname, status))
#             return 'Status updated sucessful'
#     except Exception as e:
#         print('В функции set_status что-то пошло не так:')
#         print(e)
        

def payment_success(tg_user_id,dtp_date,record_date):
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            now_date = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE `users` SET paid=1 WHERE tg_user_id=%s AND dtp_date=%s AND record_date=%s"
            cursor.execute(sql,(tg_user_id, dtp_date, record_date))
    except:
        print('В функции payment_success что-то пошло не так.')