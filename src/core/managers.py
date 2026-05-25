from django.db import models
from django.db.models import Count, Sum, OuterRef, Subquery, IntegerField, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

class ProfileManager(models.Manager):
    def get_best_for_cache(self):
        one_week_ago = timezone.now() - timedelta(days=7)

        from questions.models import Question, Answer

        questions_rating = Question.objects.filter(
            author=OuterRef('pk'),
            created_at__gte=one_week_ago
        ).values('author').annotate(
            sum_rating=Sum('rating')
        ).values('sum_rating')

        answers_rating = Answer.objects.filter(
            author=OuterRef('pk'),
            created_at__gte=one_week_ago
        ).values('author').annotate(
            sum_rating=Sum('rating')
        ).values('sum_rating')

        return self.annotate(
            q_rating=Coalesce(Subquery(questions_rating, output_field=IntegerField()), 0),
            a_rating=Coalesce(Subquery(answers_rating, output_field=IntegerField()), 0)
        ).annotate(
            total_rating=F('q_rating') + F('a_rating')
        ).filter(
            total_rating__gt=0
        ).order_by('-total_rating')[:10]


    def get_profile_stat(self, user):
        return self.get_queryset().filter(user=user).select_related('user').annotate(
            questions_count=Count('questions', distinct=True),
            answers_count=Count('answers', distinct=True),
            reputation=Sum('answers__rating', default=0)
        ).first()

    def get_top_tags(self, user, limit=5):
        from questions.models import Tag
        return Tag.objects.filter(questions__author=user.profile).annotate(tags_count=Count('questions')).order_by('-tags_count')[:limit]
