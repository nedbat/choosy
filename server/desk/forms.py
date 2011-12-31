from django.forms import ModelForm, CharField, Textarea
from desk.models import Exercise

from lxml.html.clean import Cleaner


class MultilineTextField(CharField):
    """A multi-line text field that scrubs \r from the results."""
    def __init__(self, widget=None):
        super(MultilineTextField, self).__init__(widget=widget or Textarea)

    def to_python(self, value):
        # Get rid of the Windows-specific \r
        value = value.replace('\r\n', '\n')
        # Make the text end with a newline, but no extra blank lines.
        value = value.rstrip() + '\n'
        return value


class ParanoidHtmlField(MultilineTextField):
    """A multi-line HTML editing field that doesn't trust the input."""
    def __init__(self):
        super(ParanoidHtmlField, self).__init__(widget=ParanoidHtmlTextarea)

    def to_python(self, value):
        value = Cleaner().clean_html(value)
        value = super(ParanoidHtmlField, self).to_python(value)
        return value


class ParanoidHtmlTextarea(Textarea):
    """A textarea for editing HTML when we don't trust the editor."""
    def render(self, name, value, attrs=None):
        if value:
            value = Cleaner().clean_html(value)
        return super(ParanoidHtmlTextarea, self).render(name, value, attrs)
    

class ExerciseForm(ModelForm):
    """For editing Exercises."""
    class Meta:
        model = Exercise

    text = ParanoidHtmlField()
    check = MultilineTextField()
    solution = MultilineTextField()
