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
    def from_dict(cls, d, user):
        """Create a Page from a dict representation."""
        pg, _ = cls.objects.get_or_create(slug=d['slug'], user=user)
        pg.title = d.get('title', '')
        pg.text = d.get('text', '')

        pg.nextpage_set.all().delete()
        for i, next in enumerate(d.get('nexts', ())):
            next_pg, _ = Page.objects.get_or_create(slug=next['next'], user=user)
            pg.nextpage_set.create(order=i, text=next['text'], next=next_pg)

        return pg

    @classmethod
    def from_yaml(cls, yaml_file, user):
        """Create a Page from a YAML file."""
        data = yaml.safe_load(yaml_file)
        if isinstance(data, dict):
            return cls.from_dict(data, user)
        else:
            for d in data:
                pg = cls.from_dict(d, user)
            return pg

class NextPage(models.Model):
    page = models.ForeignKey(Page)
    order = models.IntegerField()
    text = models.CharField(max_length=150)
    next = models.ForeignKey(Page, related_name='prevpage')

