from django.db import models
from django.db.models import Count, Q

class ProfileManager(models.Manager):
    def get_best(self, limit=10):
        return self.annotate(
            correct_answers_count=Count(
                'answers',
                filter=Q(answers__is_correct=True)
            )
        ).select_related('user') \
         .order_by('-correct_answers_count')[:limit]
