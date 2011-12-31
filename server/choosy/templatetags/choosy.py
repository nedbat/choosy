from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from lxml.html.clean import Cleaner


register = template.Library()

@register.filter
@stringfilter
def clean_html(value):
    cleaner = Cleaner()
    value = cleaner.clean_html(value)
    return mark_safe(value)
