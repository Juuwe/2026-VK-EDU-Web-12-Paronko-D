import smtplib
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Answer

@shared_task(bind=True, autoretry_for=(smtplib.SMTPException,), max_retries=3, retry_backoff=True)
def send_new_answer_notification_task(self, answer_id, base_url):
    try:
        answer = Answer.objects.select_related('question__author__user', 'author__user').get(id=answer_id)
    except Answer.DoesNotExist:
        return "Ответ не найден. Письмо не отправлено."

    question = answer.question
    question_author = question.author

    if question_author.id == answer.author.id:
        return "Автор ответил сам себе."

    if not question_author.user.email:
        return "У автора вопроса не указан email."

    context = {
        'author_name': question_author.nickname,
        'question_title': question.title,
        'answer_author': answer.author.nickname,
        'answer_text': answer.content,
        'question_url': f"{base_url}{question.get_absolute_url()}"
    }

    html_message = render_to_string('questions/email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=f'Новый ответ на ваш вопрос: {question.title}',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[question_author.user.email],
        html_message=html_message,
        fail_silently=False,
    )

    return f"Письмо успешно отправлено на {question_author.user.email}"
