from django import template

register = template.Library()

popular_tags = [
    {"id": i, "name": f'name:{i}'}
    for i in range(20)
]

best_users = [
    {"id": i, "nickname": f'nickname:{i}'}
    for i in range(10)
]

@register.inclusion_tag("partials/sidebar.html")
def show_sidebar():
    return {'popular_tags': popular_tags, 'best_users': best_users}
