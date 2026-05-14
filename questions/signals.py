from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.db.models import F
from django.db.models.signals import m2m_changed
from django.db import IntegrityError
from .models import Question, Tag, Answer, QuestionLike, AnswerLike

@receiver(m2m_changed, sender=Question.tags.through)
def check_tags_limit(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if pk_set and instance.tags.count() + len(pk_set) > 5:
            raise IntegrityError(
                    f"Нарушение целостности: вопрос ID {instance.pk}\n"
                    f"Вопрос может иметь максимум 5 тегов"
                )

@receiver(m2m_changed, sender=Question.tags.through)
def update_tag_questinos_count(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        Tag.objects.filter(pk__in=pk_set).update(
            questions_count=F('questions_count') + 1
        )
    elif action == "post_remove":
        Tag.objects.filter(pk__in=pk_set).update(
            questions_count=F('questions_count') - 1
        )

# @receiver(post_save, sender=QuestionLike)
# @receiver(post_save, sender=AnswerLike)
# def update_rating_on_save(sender, instance, created, **kwargs):
#     target_field = 'question' if hasattr(instance, 'question') else 'answer'
#     target_obj = getattr(instance, target_field)
#     model_class = target_obj.__class__

#     if created:
#         model_class.objects.filter(pk=target_obj.pk).update(
#             rating=F('rating') + instance.value
#         )
#     else:
#         model_class.objects.filter(pk=target_obj.pk).update(
#             rating=F('rating') + (instance.value * 2)
#         )

# @receiver(post_delete, sender=QuestionLike)
# @receiver(post_delete, sender=AnswerLike)
# def update_rating_on_delete(sender, instance, **kwargs):
#     if isinstance(instance, QuestionLike):
#         Question.objects.filter(pk=instance.question_id).update(
#             rating=F('rating') - instance.value
#         )
#     elif isinstance(instance, AnswerLike):
#         Answer.objects.filter(pk=instance.answer_id).update(
#             rating=F('rating') - instance.value
#         )

@receiver(pre_save, sender=Answer)
def track_answer_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_obj = Answer.objects.filter(pk=instance.pk).values('is_correct').first()
        instance._old_is_correct = old_obj['is_correct']
    else:
        instance._old_is_correct = False

@receiver(post_save, sender=Answer)
def update_counters(sender, instance, created, **kwargs):
    if created:
        Question.objects.filter(pk=instance.question_id).update(
            answers_count=F('answers_count') + 1
        )

    old_is_correct = instance._old_is_correct
    new_is_correct = instance.is_correct

    diff = new_is_correct - old_is_correct
    if diff != 0:
        instance.author.__class__.objects.filter(pk=instance.author_id).update(
            correct_answers_count=F('correct_answers_count') + diff
        )

@receiver(post_delete, sender=Answer)
def update_counters_on_delete(sender, instance, **kwargs):
    Question.objects.filter(pk=instance.question_id).update(
        answers_count=F('answers_count') - 1
    )

    if instance.is_correct:
        instance.author.__class__.objects.filter(pk=instance.author_id).update(
            correct_answers_count=F('correct_answers_count') - 1
        )
