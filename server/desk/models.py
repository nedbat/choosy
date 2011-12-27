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

    def as_yaml(self):
        """Return a YAML string representing this exercise."""
        # PyYaml probably has a way to do this, but I got lost in the docs.
        yaml = []
        yaml.append("name: %s\n" % self.name)
        yaml.append("text: |\n")
        for l in self.text.splitlines():
            yaml.append("  %s\n" % l)
        yaml.append("check: |\n")
        for l in self.check.splitlines():
            yaml.append("  %s\n" % l)
        return "".join(yaml)
