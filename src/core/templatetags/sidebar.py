from django import template
from django.core.cache import cache
from django.conf import settings

from core.models import Profile
from questions.models import Tag

register = template.Library()

def get_popular_tags():
    popular_tags_cache = cache.get(settings.CACHE_KEY_POPULAR_TAGS)
    if popular_tags_cache is None:
        popular_tags_cache = list(Tag.objects.get_popular_for_cache())
        cache.set(settings.CACHE_KEY_POPULAR_TAGS, popular_tags_cache, settings.SIDEBAR_CACHE_TTL)

    return popular_tags_cache

def get_best_members():
    best_members_cache = cache.get(settings.CACHE_KEY_BEST_MEMBERS)
    if best_members_cache is None:
        best_members_cache = list(Profile.objects.get_best_for_cache())
        cache.set(settings.CACHE_KEY_BEST_MEMBERS, best_members_cache, settings.SIDEBAR_CACHE_TTL)

    return best_members_cache

@register.inclusion_tag("partials/sidebar.html")
def show_sidebar():
    return {'popular_tags': get_popular_tags(),
            'best_users': get_best_members()
    }
