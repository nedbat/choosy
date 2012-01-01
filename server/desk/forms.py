from django.forms import ModelForm, CharField, Textarea
from desk.models import Exercise


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


class MarkdownField(MultilineTextField):
    """A multi-line Markdown editing field."""
    def __init__(self):
        super(MarkdownField, self).__init__(widget=MarkdownTextarea)


class MarkdownTextarea(Textarea):
    """A textarea for editing Markdown."""
    def __init__(self, attrs=None):
        cls = ""
        if attrs:
            cls = attrs.get("class", "")
        my_attrs = {}
        if attrs:
            my_attrs.update(attrs)
        my_attrs["class"] = (cls + " markdown").strip()
        super(MarkdownTextarea, self).__init__(my_attrs)


class ExerciseForm(ModelForm):
    """For editing Exercises."""
    class Meta:
        model = Exercise

    text = MarkdownField()
    check = MultilineTextField()
    solution = MultilineTextField()
