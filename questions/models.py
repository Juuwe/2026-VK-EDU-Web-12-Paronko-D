from django.utils import timezone
from django.db import models
from .managers import QuestionQuerySet, AnswerManager, TagManager, LikeManager
from . import validators
from django.urls import reverse

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector

class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(verbose_name="Имя тега", max_length=25, unique=True)
    questions_count = models.PositiveBigIntegerField(verbose_name="Кол-во вопросов", default=0)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

        ordering = ['name']

    def __str__(self):
        return self.name

class Question(models.Model):
    objects = QuestionQuerySet.as_manager()

    author = models.ForeignKey("core.Profile", verbose_name="Создатель вопроса", on_delete=models.SET_NULL, null=True, related_name="questions")
    title = models.CharField(verbose_name="Тема вопроса", max_length=100)
    content = models.TextField(verbose_name="Вопрос", max_length=1000) # уточнить maxlength
    rating = models.IntegerField(verbose_name="Рейтинг", default=0, db_index=True)
    answers_count = models.PositiveIntegerField(verbose_name="Кол-во ответов", default=0)
    created_at = models.DateTimeField(verbose_name="Дата и время создания", default=timezone.now, db_index=True)
    tags = models.ManyToManyField("questions.Tag", verbose_name="Теги вопроса", related_name="questions")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

        ordering = ['-created_at']

        indexes = [
            GinIndex(
                name='question_search_gin_idx',
                fields=['title', 'text'],
                opclasses=['gin_trgm_ops', 'gin_trgm_ops']  # Требуется расширение pg_trgm
            )
        ]

    def __str__(self):
        return f"Вопрос #{self.pk}: {self.title}"

    def clean(self):
        super().clean()

        if not self.author:
            return

        validators.validate_created_date(self.author.created_at, self.created_at, "Question.created_at: Вопрос не может быть создан раньше аккаунта автора")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('question', kwargs={'pk': self.pk})

``
class Answer(models.Model):
    objects = AnswerManager()

    author = models.ForeignKey("core.Profile", verbose_name="Создатель ответа", on_delete=models.SET_NULL, null=True, related_name="answers")
    question = models.ForeignKey("questions.Question", verbose_name="Вопрос", on_delete=models.CASCADE, related_name="answers")

    content = models.TextField(verbose_name="Ответ", max_length=1000) # уточнить maxlength
    rating = models.IntegerField(verbose_name="Рейтинг", default=0)

    created_at = models.DateTimeField(verbose_name="Дата и время создания", default=timezone.now)
    is_correct = models.BooleanField(verbose_name="Правильный?", default=False, db_index=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=models.Q(is_correct=True),
                name='unique_correct_answer_per_question'
            )
        ]

        ordering = ['-is_correct', 'created_at']

    def clean(self):
        super().clean()

        question = getattr(self, 'question', None)
        if not question:
            return

        validators.validate_created_date(self.question.created_at, self.created_at, 'Answer.created_at: Ответ не может быть создан раньше вопроса')

    def update_is_correct(self, new_is_correct):
        self.is_correct = new_is_correct
        self.save(update_field=['is_correct'])

    def update_rating(self, value):
        self.rating += value
        self.save(update_field=['rating'])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ответ {self.pk}: {self.content[:50]}..."

class Like(models.Model):
    objects = LikeManager()

    user = models.ForeignKey("core.Profile", verbose_name="Автор лайка", on_delete=models.SET_NULL, null=True, related_name="%(class)s_votes")
    created_at = models.DateTimeField(verbose_name="Дата и время создания", default=timezone.now)
    value = models.SmallIntegerField(choices=[(1, 'Лайк'), (-1, 'Дизлайк')], default=1)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

class QuestionLike(Like):
    question = models.ForeignKey("questions.Question", verbose_name="Вопрос", on_delete=models.CASCADE, related_name="likes")

    class Meta(Like.Meta):
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

        unique_together = [
            ["user", "question"]
        ]

    def clean(self):
        super().clean()
        if not self.question:
            return

        validators.validate_created_date(self.question.created_at, self.created_at, 'QuestionLike.created_at: Оценка не может быть поставлена раньше создания вопроса')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AnswerLike(Like):
    answer = models.ForeignKey("questions.Answer", verbose_name="Ответ", on_delete=models.CASCADE, related_name="likes")

    class Meta(Like.Meta):
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

        unique_together = [
            ["user", "answer"]
        ]

    def clean(self):
        super().clean()
        if not self.answer:
            return

        validators.validate_created_date(self.answer.created_at, self.created_at, 'AnswerLike.created_at: Оценка не может быть поставлена раньше создания ответа')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
