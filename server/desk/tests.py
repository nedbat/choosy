import textwrap

from django.test.client import Client
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise

class SimpleTest(ChoosyDjangoTestCase):
    def test_nothing(self):
        pass


class YamlTest(ChoosyDjangoTestCase):

    def setUp(self):
        self.ex = Exercise.objects.create(
            slug="hello-world",
            name="Hello world",
            text="<p>This is the first\nexercise. Good luck!</p>\n",
            check="def check(t, c):\n  with c.expect('Should!'):\n    c.fail('Broke!')\n",
            )
        self.ex.save()
        self.yaml = textwrap.dedent("""\
            slug: "hello-world"
            name: "Hello world"
            text: |
                <p>This is the first
                exercise. Good luck!</p>
            check: |
                def check(t, c):
                  with c.expect('Should!'):
                    c.fail('Broke!')
            """)

    def test_direct(self):
        self.assertEqual(self.ex.as_yaml(), self.yaml)

    def test_through_view(self):
        client = Client()
        response = client.get(reverse('yaml_exercise', args=[self.ex.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.yaml)
