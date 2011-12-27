from django.forms import ModelForm
from desk.models import Exercise

class ExerciseForm(ModelForm):
    class Meta:
        model = Exercise
