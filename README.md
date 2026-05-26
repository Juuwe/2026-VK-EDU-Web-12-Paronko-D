# Nginx + Gunicorn

## Что было сделано
1. Написан легковесный WSGI-скрипт для ручной обработки GET/POST параметров без использования фреймворков.
2. Настроен веб-сервер Nginx: раздача статики (`/static/`, `/uploads/`), gzip-сжатие и кэширование (`proxy_cache`).
3. Проведено нагрузочное тестирование с помощью Apache Benchmark (`ab`).

## Как запустить проект

> ### Конфигурация окружения (.env.docker)
> Для успешного быстрого запуска проекта в учебных целях все демонстрационные учетные данные и секреты вынесены ниже.
> Понимаю, что в реальной разработке так делать НЕЛЬЗЯ.
>
> Перед сборкой контейнеров создайте в корне проекта файл **`.env.docker`** и скопируйте в него следующее содержимое:
>
> ```ini
> DEBUG=True
> SECRET_KEY='django-insecure-demo-key-for-mentors-verification-2026-xyz'
> ALLOWED_HOSTS=localhost,127.0.0.1
>
> DB_ENGINE=django.db.backends.postgresql
> DB_NAME=vk_edu_web_paronko_d_db
> DB_USER=admin
> DB_PASSWORD=admin
> DB_HOST=db
> DB_PORT=5432
>
> POSTGRES_DB=vk_edu_web_paronko_d_db
> POSTGRES_USER=admin
> POSTGRES_PASSWORD=admin
>
> REDIS_HOST=redis
> REDIS_PORT=6379
>
> REDIS_CACHE_DB=0
> REDIS_BROKER_DB=1
> REDIS_BEAT_DB=2
>
> EMAIL_HOST=maildev
> EMAIL_PORT=1025
> EMAIL_USE_TLS=False
> DEFAULT_FROM_EMAIL=noreply@web_paronko.com
>
> CENTRIFUGO_TOKEN_HMAC_SECRET_KEY=dev-secret-key-for-jwt-123
> CENTRIFUGO_API_KEY=dev-api-key-for-django-456
> CENTRIFUGO_ADMIN_PASSWORD=admin
> CENTRIFUGO_ADMIN_SECRET=mentor-super-secret-session-key
> ```

1. Склонируйте репозиторий: \
    `git clone https://github.com/Juuwe/2026-VK-EDU-Web-12-Paronko-D.git`
2. Перейдите в директорию с проектом: \
    `cd 2026-VK-EDU-Web-12-Paronko-D`
3. Переключитесь на ветку hw-7: \
    `git checkout hw-7`
4. Очистите контейнеры из прошлых ДЗ с очисткой кэша: \
   `docker compose down -v`
5. Поднимите контейнеры в фоновом режиме командой: \
   `docker compose up -d --build`
6. Выполните миграции: \
    `docker compose exec web python manage.py migrate`
7. ПРИ НЕОБХОДИМОСТИ заполните БД: \
    `docker compose exec web python manage.py fill_db 1000`

## Доступы к сервисам:

1. Основное приложение проксируется через nginx: `http://localhost/`
2. Тестовый wsgi-скрипт: `http://localhost:8081/`


| № | Сценарий тестирования | RPS (запросов/сек) | Время на запрос (ms) |
|---|-----------------------|--------------------|----------------------|
| 1 | Статика через Nginx   | **3858.72** | 13                   |
| 2 | Статика через Gunicorn| **3986.04** | 12                   |
| 3 | Динамика напрямую     | **3307.15** | 13                   |
| 4 | Прокси без кэша       | **3635.75** | 13                   |
| 5 | Прокси с кэшем        | **3812.95** | 13                   |
