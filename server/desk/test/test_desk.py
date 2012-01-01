from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class DeskTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml']

    def test_index(self):
        response = self.client.get(reverse("desk"))
        self.assertTemplateUsed(response, "desk/templates/index.html")
        self.assertContains(response, "Variables")
        self.assertContains(response, "Lists")
        self.assertContains(response, "Functions")

    def test_show_exercise(self):
        response = self.client.get(reverse("desk_show_exercise", args=['functions']))
        self.assertTemplateUsed(response, "desk/templates/show_exercise.html")
        self.assertContains(response, "<li>average([1]) returns 1</li>")

    def test_script_cleaning(self):
        # User-provided HTML is cleaned before display.
        response = self.client.get(reverse("desk_show_exercise", args=['functions']))
        self.assertContains(response, "<p>This is fine, I'm sure:")
        self.assertNotContains(response, "<script>alert")


class DeskEditTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml']

    def test_edit(self):
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

    def test_new(self):
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
        self.assertQuerysetEqual(Exercise.objects.all(),
            ['<Exercise: Variables>', '<Exercise: Lists>', '<Exercise: Functions>', '<Exercise: A New Exercise!>']
            )
        ex = Exercise.objects.get(slug='brand-new')
        # While editing, your markdown will still have malicious stuff in it.
        self.assertEqual(ex.text, '<p>What could go wrong?<script>alert("danger")</script> It should be fine.</p>\n')
        self.assertEqual(ex.check, "def check(t, c):\n    pass\n")
