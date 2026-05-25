from django.db import models
from django.db.models import F, Value, Count

from django.db.models import Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

class QuestionQuerySet(models.QuerySet):
    def with_user_vote(self, user):
        if not user or not user.is_authenticated:
            return self.annotate(user_vote=Value(0, output_field=IntegerField()))

        from .models import QuestionLike
        user_vote_subquery = QuestionLike.objects.filter(
            question=OuterRef('pk'),
            user=user.profile
        ).values('value')

        return self.annotate(
            user_vote=Coalesce(
                Subquery(user_vote_subquery[:1]),
                Value(0),
                output_field=IntegerField()
            )
        )

    def hot(self):
        return self.order_by('-rating')

    def tag(self, tag_name):
        return self.filter(tags__name=tag_name)

class AnswerQuerySet(models.QuerySet):
    def with_user_vote(self, user):
        if not user or not user.is_authenticated:
            return self.annotate(user_vote=Value(0, output_field=IntegerField()))


        from .models import AnswerLike
        user_vote_subquery = AnswerLike.objects.filter(
            answer=OuterRef('pk'),
            user=user.profile
        ).values('value')

        return self.annotate(
            user_vote=Coalesce(
                Subquery(user_vote_subquery[:1]),
                Value(0),
                output_field=IntegerField()
            )
        )

    def best(self):
        return self.order_by('-is_correct', '-rating', 'created_at')

class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def with_user_vote(self, user):
        return self.get_queryset().with_user_vote(user)

    def best(self):
        return self.get_queryset().best()

    def toggle_correct(self, user, answer_id):
        try:
            answer = self.select_related('question').get(pk=answer_id)
        except self.model.DoesNotExist:
            return None, "Answer does not exist"

        if answer.question.author != user.profile:
            return None, "Only authors can toggle correct"

        if not answer.is_correct:
            self.filter(question=answer.question, is_correct=True).update(is_correct=False)

        answer.is_correct = not answer.is_correct

        answer.save(update_fields=['is_correct'])

        return answer.is_correct, None


class TagManager(models.Manager):
    def popular(self, limit=20):
        return self.order_by('-questions_count')[:limit]

    def get_popular_for_cache(self, limit=20):
        three_months_ago = timezone.now() - timedelta(days=90)

        return self.filter(
            questions__created_at__gte=three_months_ago
        ).annotate(
            recent_questions_count=Count('questions')
        ).order_by('-recent_questions_count')[:10]

class LikeManager(models.Manager):
    def add_vote(self, user, object, new_value):
        field_name = 'question' if hasattr(self.model, 'question') else 'answer'
        like = self.filter(user=user, **{field_name: object}).first()

        delta = 0
        action = 'like' if new_value == 1 else 'dislike'
        if like:
            if like.value == new_value:
                delta = -like.value
                like.delete()
                action = 'deleted'
            else:
                delta = new_value - like.value
                like.value = new_value
                like.save()
        else:
            delta = new_value
            self.create(user=user, **{field_name: object}, value=new_value)

        if delta != 0:
            object.__class__.objects.filter(pk=object.pk).update(rating=F('rating') + delta)
            object.refresh_from_db()

        return action
