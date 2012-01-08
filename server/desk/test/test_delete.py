from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class DeleteTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml', 'users.yaml']

    def setUp(self):
        super(DeleteTest, self).setUp()
        self.user = User.objects.get(username='basicauthor')

    def test_deleting_exercise(self):
        self.login()
        self.assertQuerysetEqual(Exercise.objects.filter(user=self.user), ['<Exercise: Variables>', '<Exercise: Lists>', '<Exercise: Functions>'])
        ex = Exercise.objects.get(slug="lists")
        response = self.client.post(reverse("delete_exercise", args=[ex.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(Exercise.objects.filter(user=self.user), ['<Exercise: Variables>', '<Exercise: Functions>'])

    def test_cant_delete_anothers_exercise(self):
        self.login()
        ex = Exercise.objects.get(slug="otherexercise")
        response = self.client.post(reverse("delete_exercise", args=[ex.id]), {})
        self.assertEqual(response.status_code, 403)

    def test_deleting_requires_post(self):
        self.login()
        ex = Exercise.objects.get(slug="functions")
        response = self.client.get(reverse("delete_exercise", args=[ex.id]))
        self.assertEqual(response.status_code, 405)

    def test_cant_delete_exercise_anonymously(self):
        ex = Exercise.objects.get(slug="lists")
        url = reverse("delete_exercise", args=[ex.id])
        response = self.client.post(url, {})
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))
