## Проект будет использоваться компанией .  

Скрипт,mysql,phpmyadmin,контейнер с миграциями на сервере работает в docker-compose используется файл docker-compose-production.yaml.


Редми немного не актуальный
## Библиотеки
    YaDiskClient
    dataclasses
    остальное в reqirments.txt

## Переменные среды
Для работы приложения необходимо разместить в файле .env. Переменные среды.По умолчанию они находятся в файле  env_default.

IFACE=127.0.0.1 -интерфейс для проброса mysql порта  
PHP_ADMIN_PORT=88 - пхп админ порт для локальной разработки  
MYSQL_PORT_OUT=33069 - проброс порта mysql  
DATABASE_USERNAME=root  
DATABASE_PASSWORD= - пароль для доступа питона и mysql  
DATABASE_HOST=mysql -если работаем из докера хост mysq,если из вне то 127.0.0.1  
DATABASE_PORT=3306 -если работаем из докера порт 3306 mysq,если из вне то 33069  
DATABASE_NAME=ai_bot - имя базы данных для доступа питона и mysql
DATABASE_HOST_MIGRATIONS - имя хоста для миграций (приразработке проще использовать разные переменые), default: mysql
DATABASE_PORT_MIGRATIONS -тоже самое. default:3306
#PROD BOT  
BOT_TOKEN= -токен доступа к боту  
YANDEX_DISK_TOKEN - яндекс токен OAuth выдается на год  
PROD=False - True / False обозначение для логов, если True загружается анкету и фото на яндекс диск

YOOMONEY_SERVICE_PRICE=2 - цена за услугу на YOOMONEY.Валюта рубли
YOOMONEY_WALLET_TOKEN=  - токен YOOMONEY
YOOMONEY_RECEIVER= id получателя берется из лк YOOMONEY.
Статья по получению токена на [YOOMONEY](https://habr.com/ru/post/558924/)

## Develop
Для обновления списка пакетов в requirements.txt используем pipreqs ./project_path  
``` pipreqs ./ --force```

    Для загрузки в переменую окружения из .env можно использовать bash run.sh
     или
    #!/usr/bin/env bash
    set -a;source .env;set +a
    Для запуска бота без докера.  
Запускать в папке с файлами docker-compose.yaml

Запуск контейнеров в фоновом режиме без запуска бота для разработки  
```docker-compose up -d ```  
C опцией --build контейнеры пересоберутся  
```docker-compose up -d --build```  
Для удаления всех данных после изменения docker-compose  
``` docker-compose down -v --remove-orphans ```  
Для сборки продакшен docker-compose  
```docker-compose -f docker-compose-production.yaml up -d --build```
Посмотреть запущенные контейнеры
```docker ps```
### Запуск миграций  
Истинный файл миграций db_class.py в папке libs
Редактируем его, а затем автогенерируем миграции.
Доступ к базе через переменные среды.
DATABASE_HOST_MIGRATIONS
DATABASE_PORT_MIGRATIONS
Локально:
Запуск миграций  
```  alembic upgrade head ```  
Создание новой миграции    
``` alembic revision --autogenerate -m 'Name for migratiob' ```   
Запуск миграции в контейнере
``` docker-compose -p ai_bot_mysql up``` не доработанно  
 
### backend
Читаем таски берем одну и обрабатываем на клиенте.
Возвращает телеграм юзер айди
``` curl http://localhost:5000/rest/v1/get_task ```
Сохранение фото
``` curl -X POST http://localhost:5000/rest/v1/get_photo_to_render --output output_photo.jpg -H "Content-Type: application/json" -d '{"tg_user_id": 166889867}' ```
Замена статуса
``` curl -X POST http://localhost:5000/rest/v1/set_status -H "Content-Type: application/json" -d '{"status": "rendirng", "tg_user_id": 166889867}' ```
Нужно добавить будет столбец времени рендрина и высчитывать и записывать