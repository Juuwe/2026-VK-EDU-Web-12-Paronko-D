FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000 8081

CMD ["gunicorn", "-c", "gunicorn.conf.py", "application.wsgi:application"]
