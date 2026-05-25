FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system webgroup && adduser --system --ingroup webgroup webuser

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN chown -R webuser:webgroup /app

USER webuser

EXPOSE 8000 8081

CMD ["gunicorn", "-c", "gunicorn.conf.py", "application.wsgi:application"]
