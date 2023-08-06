from os import environ, path
from dotenv import load_dotenv
 
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
 
 
# Database config fronm env
db_user = environ.get('DATABASE_USERNAME')
db_password = environ.get('DATABASE_PASSWORD')
db_host = environ.get('DATABASE_HOST')
db_port = environ.get('DATABASE_PORT')
db_name = environ.get('DATABASE_NAME')
 
db_host_migrations = environ.get('DATABASE_HOST_MIGRATIONS')

bot_token = environ.get('BOT_TOKEN')

yandex_disk_token = environ.get('YANDEX_DISK_TOKEN')
#yoomoney credentials
ym_wallet_token = environ.get('YOOMONEY_WALLET_TOKEN')
ym_service_price = environ.get('YOOMONEY_SERVICE_PRICE')
ym_receiver = environ.get('YOOMONEY_RECEIVER')


# chat for logs
# logs_chat=environ.get('LOGS_CHAT')
# manager_chat=environ.get('MANAGER_CHAT')
 
if environ.get('PROD').lower() == 'true':
    stage='PROD'
else:
    stage='DEV'