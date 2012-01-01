from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

import markdown as markdown_mod
import pygments

register = template.Library()

@register.filter
@stringfilter
def markdown(value):
    """
    Runs Markdown over a given value.

    Syntax::

        {{ value|markdown }}

    """
    return mark_safe(markdown_mod.markdown(force_unicode(value), ["codehilite"], safe_mode="remove"))
markdown.is_safe = True


@register.filter
@stringfilter
def syntax_color(value):
    """Syntax-color a value with Pygments."""
    try:
        lexer = pygments.lexers.guess_lexer(value)
    except ValueError:
        lexer = pygments.lexers.PythonLexer()
    return mark_safe(pygments.highlight(force_unicode(value), lexer, pygments.formatters.HtmlFormatter()))
syntax_color.is_safe = True
