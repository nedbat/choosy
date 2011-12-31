"""Hide some details of HTML manipulation."""

from lxml.html.clean import Cleaner

def clean_html(html):
    cleaner = Cleaner()
    return cleaner.clean_html(html)
