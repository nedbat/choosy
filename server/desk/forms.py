from django.forms import ModelForm
from gym.models import Exercise

class ExerciseForm(ModelForm):
    class Meta:
        model = Exercise
