from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class DeskTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml', 'tricky_html.yaml']

    def test_show_exercise(self):
        response = self.client.post(reverse("desk_show_exercise", args=['functions']), {})
        self.assertTemplateUsed(response, "desk/templates/show_exercise.html")
        self.assertContains(response, "<li>average([1]) returns 1</li>")

    def test_script_cleaning(self):
        # User-provided HTML is cleaned before display.
        response = self.client.post(reverse("desk_show_exercise", args=['alert-xss']), {})
        self.assertContains(response, "<p>This is fine, I'm sure:")
        self.assertNotContains(response, "danger")
