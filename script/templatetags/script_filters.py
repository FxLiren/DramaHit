from django import template
import re

register = template.Library()


@register.filter
def remove_votes(value):
    return re.sub(r'/\s*[0-9]+\s*票$', '', value)