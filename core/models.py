from django.utils import timezone
from django.db import models
from .managers import ProfileManager
from .utils import get_avatar_upload_path
from django.core.validators import FileExtensionValidator
from .validators import validate_file_size


class Profile(models.Model):
    objects = ProfileManager()

    user = models.OneToOneField("auth.User", verbose_name="Аккаунт", on_delete=models.CASCADE, related_name='profile')

    nickname = models.CharField(verbose_name="Никнейм", max_length=50, unique=True)
    avatar = models.ImageField(verbose_name="Аватар", upload_to=get_avatar_upload_path, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png']), validate_file_size])
    created_at = models.DateTimeField(verbose_name="Дата и время создания", default=timezone.now)

    correct_answers_count = models.PositiveIntegerField(verbose_name="Кол-во правильных ответов", default=0)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.nickname
