from django.utils import timezone
from django.db import models
from .managers import ProfileManager

class Profile(models.Model):
    objects = ProfileManager()

    user = models.OneToOneField("auth.User", verbose_name="Аккаунт", on_delete=models.CASCADE, related_name='profile')

    nickname = models.CharField(verbose_name="Никнейм", max_length=50, unique=True)
    avatar = models.ImageField(verbose_name="Аватар", upload_to="", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Дата и время создания", default=timezone.now)

    correct_answers_count = models.PositiveIntegerField(verbose_name="Кол-во правильных ответов", default=0)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.nickname
