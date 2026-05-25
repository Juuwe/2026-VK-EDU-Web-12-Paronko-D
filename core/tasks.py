from celery import shared_task
from django.core.cache import cache
from django.conf import settings

from questions.models import Tag
from core.models import Profile

@shared_task
def update_popular_tags_cache_task():
    popular_tags_cache = Tag.objects.get_popular_for_cache()
    cache.set(settings.CACHE_KEY_POPULAR_TAGS, popular_tags_cache, settings.CACHE_TTL)
    return 'Кэш популярных тегов обновлен'

@shared_task
def update_best_member_cache_task():
    best_members_cache = Profile.objects.get_best_for_cache()
    cache.set(settings.CACHE_KEY_BEST_MEMBERS, best_members_cache, settings.CACHE_TTL)
    return 'Кэш лучших пользователей обновлен'
