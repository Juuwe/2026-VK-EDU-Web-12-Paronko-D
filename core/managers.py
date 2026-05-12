from django.db import models
from django.db.models import Count, Sum

class ProfileManager(models.Manager):
    def get_best(self, limit=10):
        return self.select_related('user').order_by('-correct_answers_count')[:limit]

    def get_profile_stat(self, user):
        return self.get_queryset().filter(user=user).select_related('user').annotate(
            questions_count=Count('questions', distinct=True),
            answers_count=Count('answers', distinct=True),
            reputation=Sum('answers__rating', default=0)
        ).first()

    def get_top_tags(self, user, limit=5):
        from questions.models import Tag
        return Tag.objects.filter(questions__author=user.profile).annotate(tags_count=Count('questions')).order_by('-tags_count')[:limit]
