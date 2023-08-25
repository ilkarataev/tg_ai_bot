import os
from os import environ, path
from dotenv import load_dotenv
 
basedir = path.abspath(path.dirname(__file__))

load_dotenv(path.join(basedir, '../.env'))

# Database config fronm env
db_user = os.environ.get('DATABASE_USERNAME')
db_password = os.environ.get('DATABASE_PASSWORD')
db_host = os.environ.get('DATABASE_HOST')
db_port = os.environ.get('DATABASE_PORT')
db_name = os.environ.get('DATABASE_NAME')
 
db_host_migrations = os.environ.get('DATABASE_HOST_MIGRATIONS')

bot_token = os.environ.get('BOT_TOKEN')

yandex_disk_token = os.environ.get('YANDEX_DISK_TOKEN')
#yoomoney credentials
ym_wallet_token = os.environ.get('YOOMONEY_WALLET_TOKEN')
ym_service_price = os.environ.get('YOOMONEY_SERVICE_PRICE')
ym_receiver = os.environ.get('YOOMONEY_RECEIVER')


# chat for logs
# logs_chat=environ.get('LOGS_CHAT')
# manager_chat=environ.get('MANAGER_CHAT')
 
if os.environ.get('PROD').lower() == 'true':
    stage='PROD'
else:
    stage='DEV'