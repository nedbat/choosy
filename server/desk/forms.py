from django.forms import ModelForm, CharField, Textarea
from desk.models import Exercise


class MultilineTextField(CharField):
    """A multi-line text field that scrubs \r from the results."""
    def __init__(self):
        super(MultilineTextField, self).__init__(widget=Textarea)

    def to_python(self, value):
        # Get rid of the Windows-specific \r
        value = value.replace('\r\n', '\n')
        # Make the text end with a newline, but no extra blank lines.
        value = value.rstrip() + '\n'
        return value


class ExerciseForm(ModelForm):
    """For editing Exercises."""
    class Meta:
        model = Exercise

    text = MultilineTextField()
    check = MultilineTextField()
