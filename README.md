# ДЗ№5. Загрузка картинок и обработка AJAX запросов

1. **Клонируйте репозиторий:** \
   `git clone https://github.com/Juuwe/2026-VK-EDU-Web-12-Paronko-D.git`

2. **Перейдите в директорию с проектом:** \
   `cd 2026-VK-EDU-Web-12-Paronko-D`

3. **Переключитесь на ветку hw-4:** \
   `git checkout hw-5`

4. **Подготвьте переменные окружения:** \
   `.env.example` - Шаблон конфигурации. Содержит список всех необходимых переменных для запуска \
   `.env.local` - Нужен для локального запуска сервера. Позволяет выполнять все команды django прямо из терминала \
   `.env.docker` - Используется Docker для проброса переменных внутрь контейнера

5. **Запустите проект:**
   #### Запуск через Docker:
   `docker compose up --build` (предварительно подготовьте .env.docker) \
   `docker compose exec web python manage.py migrate` - для выполнения миграции \
   `docker compose exec web python manage.py createsuperuser` - для создания администратора \
   **При отсутствии .env.local все команды django должны выполняться только внутри контейнера**

   #### Локальный запуск:
   `python3 -m venv .venv` \
   `source .venv/bin/activate` \
   `pip install -r requirements.txt` \
   Запустите PostgreSQL локально или с помощью Docker: `docker compose up -d db` \
   Запустите веб-сервер: \
   `ENV_FILE=.env.local python manage.py migrate` \
   `ENV_FILE=.env.local python manage.py runserver`
   Создание администратора: \
    `ENV_FILE=.env.local python manage.py createsuperuser`
6. **Наполнение данными:** \
   **(Процесс наполнения данными может занять более 4 минут)**

   Для Docker:
   `docker compose exec web python manage.py fill_db 10000`

   Локально:
   `ENV_FILE=.env.local python manage.py fill_db 10000`
