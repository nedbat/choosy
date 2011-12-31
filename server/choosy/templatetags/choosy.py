from django import template
from django.template.defaultfilters import stringfilter

from lxml.html.clean import Cleaner


register = template.Library()

@register.filter
@stringfilter
def clean_html(value):
    """Clean the HTML in `value`, because we don't trust it, but need to put it on the page."""
    cleaner = Cleaner()
    value = cleaner.clean_html(value)
    return value
