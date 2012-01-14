import textwrap
import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from scrib.models import Page, NextPage


PG_SLUG = "hello-world"
PG_TITLE = "Hello world"
PG_TEXT = "This is the first\npage. Hello world!\n"

PG_YAML = textwrap.dedent("""\
    slug: "hello-world"
    title: "Hello world"
    text: |
        This is the first
        page. Hello world!
    nexts:
        -
            text: The next page
            next: second-page
        -
            text: Something else
            next: last-page
    """)


class YamlImportTest(ChoosyDjangoTestCase):

    fixtures = ['users.yaml']

    def test_importing_page(self):
        self.assertEqual(0, Page.objects.count())

        # Visit the import page
        self.login()
        response = self.client.get(reverse('import_page'))
        self.assertEqual(response.status_code, 200)

        # Post to the import page.
        yaml_file = StringIO.StringIO(PG_YAML)
        yaml_file.name = "test_yaml.yaml"
        response = self.client.post(reverse('import_page'), {'yamlfile': yaml_file}, follow=True) 

        pg = Page.objects.get(slug=PG_SLUG)
        self.assertEqual(pg.title, PG_TITLE)
        self.assertEqual(pg.text, PG_TEXT)

        self.assertRedirects(response, reverse('show_page', args=[pg.id]))

        slugs = [np.next.slug for np in NextPage.objects.filter(page=pg).order_by('order')]
        self.assertEqual(slugs, ['second-page', 'last-page'])
