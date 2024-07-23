# templatetags/time_format.py
from django import template

register = template.Library()

@register.filter
def time_format(value):
    return value.strftime('%H:%M')
