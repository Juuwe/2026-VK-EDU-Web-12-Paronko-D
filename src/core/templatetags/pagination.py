from django import template

register = template.Library()

@register.inclusion_tag("partials/pagination.html", takes_context=True)
def show_pagination(context, page_obj, on_each_side=2, on_ends=1):
    paginator = page_obj.paginator

    page_range = paginator.get_elided_page_range(
        page_obj.number,
        on_each_side=on_each_side,
        on_ends=on_ends
    )

    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'request': context.get('request')
    }
