# ДЗ№6. Дополнительные функции

* **Инфраструктура:** Развернуты Docker-контейнеры для Django, PostgreSQL, Redis, Celery, Celery Beat, Centrifugo и Maildev. Для Redis настроено использование трех изолированных баз данных (брокер, кэш, расписание).
* **Real-time обновления:** Интегрирован Centrifugo v5. Реализована мгновенная доставка новых ответов по WebSockets с обработкой пагинации и защитой от дублирования сообщений.
* **Фоновые задачи (Celery):** Настроена асинхронная отправка email-уведомлений авторам вопросов при появлении новых ответов.
* **Кэширование (Celery Beat):** Внедрен RedBeat для фонового пересчета популярности тегов (за 90 дней) и лучших пользователей (за 7 дней) через агрегацию БД. Настроено сохранение данных в Redis с fallback-механизмом.
* **Полнотекстовый поиск:** Реализован поиск средствами PostgreSQL с использованием `SearchVectorField` и `GinIndex`. На клиенте добавлен виджет автодополнения с оптимизацией запросов (debounce, AbortController).

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
3. Переключитесь на ветку hw-6: \
    `git checkout hw-6`
4. Очистите контейнеры из прошлых ДЗ с очисткой кэша: \
   `docker compose down -v`
5. Поднимите контейнеры в фоновом режиме командой: \
   `docker compose up -d --build`
6. Выполните миграции: \
    `docker compose exec web python manage.py migrate`
7. ПРИ НЕОБХОДИМОСТИ заполните БД: \
    `docker compose exec web python manage.py fill_db 1000`

## Доступы к сервисам:

1. Основное приложение: `http://localhost:8000/`
2. Админка Centrifugo: `http://localhost:8001/`
