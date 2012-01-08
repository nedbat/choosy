from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class DeskTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml', 'users.yaml']

    def test_index(self):
        self.login()
        response = self.client.get(reverse("desk"))
        self.assertTemplateUsed(response, "desk/templates/index.html")
        self.assertContains(response, "Variables")
        self.assertContains(response, "Lists")
        self.assertContains(response, "Functions")
        self.assertNotContains(response, "Other Exercise")

    def test_index_requires_login(self):
        url = reverse("desk")
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

    def test_show_exercise(self):
        self.login()
        response = self.client.get(reverse("desk_show_exercise", args=['functions']))
        self.assertTemplateUsed(response, "desk/templates/show_exercise.html")
        self.assertContains(response, "<li>average([1]) returns 1</li>")

    def test_cant_show_exercise_anonymously(self):
        url = reverse("desk_show_exercise", args=['functions'])
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

    def test_cant_show_others_exercises(self):
        self.login()
        url = reverse("desk_show_exercise", args=['otherexercise'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_script_cleaning(self):
        self.login()
        # User-provided HTML is cleaned before display.
        response = self.client.get(reverse("desk_show_exercise", args=['functions']))
        self.assertContains(response, "<p>This is fine, I'm sure:")
        self.assertNotContains(response, "<script>alert")


class DeskEditTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml', 'users.yaml']

    def setUp(self):
        super(DeskEditTest, self).setUp()
        self.user = User.objects.get(username="basicauthor")

    def test_edit(self):
        self.login()
        # Get the edit page
        response = self.client.get(reverse("edit_exercise", args=['functions']))
        self.assertContains(response, "\nThis is fine, I&#39;m sure:")
        # While editing, your markdown will still have malicious stuff in it.
        self.assertContains(response, "<script>")
        self.assertContains(response, '<form action="." method="post">')

        # Post new content.
        response = self.client.post(reverse("edit_exercise", args=['functions']), {
            'slug': 'functions',
            'name': 'Functions New',
            'text': '<p>What could go wrong?<script>alert("danger")</script> It should be fine.</p>',
            'check': 'def check(t, c):\n    pass\n',
            'solution': '',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
    
        # The exercise has changed!
        ex = Exercise.objects.get(slug='functions')
        self.assertEqual(ex.name, "Functions New")
        # While editing, your markdown will still have malicious stuff in it.
        self.assertEqual(ex.text, '<p>What could go wrong?<script>alert("danger")</script> It should be fine.</p>\n')

    def test_cant_edit_exercise_anonymously(self):
        url = reverse("edit_exercise", args=['functions'])
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

    def test_cant_edit_others_exercises(self):
        self.login()
        url = reverse("edit_exercise", args=['otherexercise'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_new(self):
        self.login()
        # Get the edit page
        response = self.client.get(reverse("new_exercise"))
        self.assertContains(response, '<form action="." method="post">')

        # Post new content
        response = self.client.post(reverse("new_exercise"), {
            'slug': 'brand-new',
            'name': 'A New Exercise!',
            'text': '<p>What could go wrong?<script>alert("danger")</script> It should be fine.</p>',
            'check': 'def check(t, c):\n    pass\n',
            'solution': '',
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        # There's a new exercise.
        self.assertQuerysetEqual(Exercise.objects.filter(user=self.user),
            ['<Exercise: Variables>', '<Exercise: Lists>', '<Exercise: Functions>', '<Exercise: A New Exercise!>']
            )
        ex = Exercise.objects.get(slug='brand-new')
        # While editing, your markdown will still have malicious stuff in it.
        self.assertEqual(ex.text, '<p>What could go wrong?<script>alert("danger")</script> It should be fine.</p>\n')
        self.assertEqual(ex.check, "def check(t, c):\n    pass\n")

    def test_cant_create_exercise_anonymously(self):
        url = reverse("new_exercise")
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

        response = self.client.post(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))
