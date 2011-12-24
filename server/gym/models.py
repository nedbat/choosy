from django.db import models
from django.template.defaultfilters import slugify

class Exercise(models.Model):
    name = models.CharField(max_length=40)
    text = models.TextField()
    check = models.TextField()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('gym_show_exercise', [str(self.id), slugify(self.name)])
