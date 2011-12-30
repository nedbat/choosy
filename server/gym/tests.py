"""Tests of gym views."""

import textwrap

from django.test.client import Client
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


class GymTest(ChoosyDjangoTestCase):

    def setUp(self):
        self.client = Client()

        self.ex1 = Exercise.objects.create(
            slug="test1",
            name="First test",
            text="<p>First!</p>",
            check=textwrap.dedent("""\
                def check(t, c):
                    with c.expect("First"):
                        c.test(t.names() == ['a'], "No a: %s" % t.names())
                """),
            solution="a = 17",
            )

        self.ex2 = Exercise.objects.create(
            slug="test2",
            name="Second test",
            text="<p>Second!</p>",
            check=textwrap.dedent("""\
                def check(t, c):
                    with c.expect("First"):
                        c.test(t.names() == ['a'], "No a: %s" % t.names())
                """),
            solution="b = 17",
            )

    def test_index(self):
        response = self.client.get(reverse('gym'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gym/templates/index.html")
        self.assertQuerysetEqual(response.context['exes'], ['<Exercise: First test>', '<Exercise: Second test>'])

    def test_show_exercise(self):
        response = self.client.get(reverse('gym_show_exercise', args=[self.ex1.id, self.ex1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gym/templates/exercise.html")
        self.assertEqual(response.context['ex'].id, self.ex1.id)

    def test_run_must_post(self):
        # The /gym/run endpoint requires a POST
        response = self.client.get(reverse('gym_run', args=[self.ex1.id]))
        self.assertEqual(response.status_code, 405)

    def test_run_successful(self):
        response = self.client.post(reverse('gym_run', args=[self.ex1.id]), {'code': 'a = 17'})
        self.assertJsonEqual(response, 
            {'status': 'ok', 'checks': [{'status': 'OK', 'expect': 'First'}], 'stdout': ''}
            )

    def test_run_unsuccessful(self):
        response = self.client.post(reverse('gym_run', args=[self.ex1.id]), {'code': 'xx = 17'})
        self.assertJsonEqual(response, 
            {'status': 'ok', 'checks': [{'status': 'FAIL', 'expect': 'First', 'did': "No a: ['xx']"}], 'stdout': ''}
            )

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
