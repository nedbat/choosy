from django import template
from django.template.defaultfilters import stringfilter

import util.html


register = template.Library()

@register.filter
@stringfilter
def clean_html(value):
    """Clean the HTML in `value`, because we don't trust it, but need to put it on the page."""
    return util.html.clean_html(value)
