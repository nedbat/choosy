"""Tests of gym views."""

import textwrap

from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class GymTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml']

    def test_index(self):
        response = self.client.get(reverse('gym'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gym/templates/index.html")
        self.assertQuerysetEqual(response.context['exes'], ['<Exercise: Variables>', '<Exercise: Lists>', '<Exercise: Functions>'])

    def test_show_exercise(self):
        response = self.client.get(reverse('gym_show_exercise', args=[1, "variables"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gym/templates/exercise.html")
        self.assertEqual(response.context['ex'].id, 1)

    def test_show_dangerous_html(self):
        response = self.client.post(reverse("gym_show_exercise", args=[3, 'functions']), {})
        self.assertContains(response, "<p>This is fine, I'm sure:")
        self.assertNotContains(response, "danger")

class GymRunTest(ChoosyDjangoTestCase):

    fixtures = ['basic.yaml']

    def test_run_must_post(self):
        # The /gym/run endpoint requires a POST
        response = self.client.get(reverse('gym_run', args=[1]))
        self.assertEqual(response.status_code, 405)

    def test_run_successful(self):
        response = self.client.post(reverse('gym_run', args=[1]), {'code': 'y = 13'})
        self.assertJsonEqual(response, {'status': 'ok', 'stdout': '',
            'checks': [
                {'status': 'OK', 'expect': 'You should have a variable named y.'},
                {'status': 'OK', 'expect': 'y should be 13.'},
                ],
            })

    def test_run_unsuccessful(self):
        response = self.client.post(reverse('gym_run', args=[1]), {'code': 'xx = 17'})
        self.assertJsonEqual(response, {'status': 'ok', 'stdout': '',
            'checks': [
                {'status': 'FAIL', 'expect': 'You should have a variable named y.', 'did': "You have a variable named xx."},
                ],
            })

    def test_run_anonymous(self):
        # /gym/run can accept the student and teacher code, for testing while editing exercises.
        response = self.client.post(reverse('gym_run_anon'), {
            'code': 'anon = 12',
            'check': textwrap.dedent("""\
                def check(t, c):
                    with c.expect("anon should be 12"):
                        anon = getattr(t.module, "anon", "Nothing")
                        c.test(anon == 12, "It was %r!" % anon)
                """)
            })
        self.assertJsonEqual(response,
            {'status': 'ok', 'checks': [{'status': 'OK', 'expect': 'anon should be 12'}], 'stdout': ''}
            )

    def test_run_must_have_check_code_somehow(self):
        response = self.client.post(reverse('gym_run_anon'), {'code': 'anon = borked'})
        self.assertEqual(response.status_code, 400)
