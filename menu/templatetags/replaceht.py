from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def replaceht(value):
    return mark_safe(value.replace('h_start', "<span style='color:#b62a00;'>").replace('h_end', "</span>"))

