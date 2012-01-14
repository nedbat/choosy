from django.contrib.auth.models import User
from django.db import models

import yaml

class Page(models.Model):
    user = models.ForeignKey(User)
    slug = models.CharField(max_length=150, unique=True)
    title = models.CharField(max_length=150)
    text = models.TextField()

    def __unicode__(self):
        return self.title or (u"Untitled: %s" % self.slug)

    @classmethod
    def from_yaml(cls, yaml_file, user):
        """Create a Page from a YAML file."""
        data = yaml.load(yaml_file)
        pg, _ = cls.objects.get_or_create(slug=data['slug'], user=user)
        pg.title = data.get('title', '')
        pg.text = data.get('text', '')

        pg.nextpage_set.all().delete()
        for i, next in enumerate(data.get('nexts', ())):
            next_pg, _ = Page.objects.get_or_create(slug=next['next'], user=user)
            pg.nextpage_set.create(order=i, text=next['text'], next=next_pg)

        return pg

class NextPage(models.Model):
    page = models.ForeignKey(Page)
    order = models.IntegerField()
    text = models.CharField(max_length=150)
    next = models.ForeignKey(Page, related_name='prevpage')

