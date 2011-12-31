from django.test.client import Client
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class DeleteTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml']

    def test_deleting_exercise(self):
        self.assertQuerysetEqual(Exercise.objects.all(), ['<Exercise: Variables>', '<Exercise: Lists>', '<Exercise: Functions>'])
        ex = Exercise.objects.get(slug="lists")
        client = Client()
        response = client.post(reverse("delete_exercise", args=[ex.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(Exercise.objects.all(), ['<Exercise: Variables>', '<Exercise: Functions>'])

    def test_deleting_requires_post(self):
        ex = Exercise.objects.get(slug="functions")
        client = Client()
        response = client.get(reverse("delete_exercise", args=[ex.id]))
        self.assertEqual(response.status_code, 405)
