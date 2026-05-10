from django import template

from core.models import Profile
from questions.models import Tag

register = template.Library()

@register.inclusion_tag("partials/sidebar.html")
def show_sidebar():
    return {'popular_tags': Tag.objects.popular(),
            'best_users': Profile.objects.get_best()
    }
