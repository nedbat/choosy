import json
from django.test import TestCase

class ChoosyDjangoTestCase(TestCase):
    """Commonality for all Choosy tests."""

    def login(self, username='basicauthor', password='play'):
        self.assertTrue(self.client.login(username=username, password=password))

    def assertJsonEqual(self, response, jsonout):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        self.assertEqual(json.loads(response.content), jsonout)
