from django import template
from django.core.cache import cache

from core.models import Profile
from questions.models import Tag

register = template.Library()

CACHE_KEY_POPULAR_TAGS = 'popular_tags_cache'
CACHE_KEY_BEST_MEMBERS = 'best_members_cache'
CACHE_TTL = 60 * 60 * 24

def get_popular_tags():
    popular_tags_cache = cache.get(CACHE_KEY_POPULAR_TAGS)
    if popular_tags_cache is None:
        popular_tags_cache = ...
        cache.set(CACHE_KEY_POPULAR_TAGS, popular_tags_cache, CACHE_TTL)

    return popular_tags_cache

@register.inclusion_tag("partials/sidebar.html")
def show_sidebar():
    return {'popular_tags': Tag.objects.popular(),
            'best_users': Profile.objects.get_best()
    }
