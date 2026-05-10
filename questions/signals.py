from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Question
from .models import QuestionLike, AnswerLike

@receiver(m2m_changed, sender=Question.tags.through)
def check_tags_limit(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if pk_set and instance.tags.count() + len(pk_set) > 5:
            raise ValidationError({'QuestionTags.check_tags_limit': "У одного вопроса не может быть больше 5 тегов"})
