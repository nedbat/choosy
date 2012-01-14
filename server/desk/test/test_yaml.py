import textwrap
import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from util.test import ChoosyDjangoTestCase
from desk.models import Exercise


EX_SLUG = "hello-world"
EX_NAME = "Hello world"
EX_TEXT = "This is the first\nexercise. Good luck!\n"
EX_CHECK = "def check(t, c):\n    with c.expect('Should!'):\n        c.fail('Broke!')\n"
EX_SOLUTION = "x = 12\ny = 13\n"

EX_YAML = textwrap.dedent("""\
    slug: "hello-world"
    name: "Hello world"
    text: |
        This is the first
        exercise. Good luck!
    check: |
        def check(t, c):
            with c.expect('Should!'):
                c.fail('Broke!')
    solution: |
        x = 12
        y = 13
    """)

class YamlExportTest(ChoosyDjangoTestCase):

    fixtures = ['users.yaml', 'basic.yaml']

    def setUp(self):
        super(YamlExportTest, self).setUp()
        self.user = User.objects.get(username='basicauthor')
        self.ex = Exercise.objects.create(
            user=self.user,
            slug=EX_SLUG,
            name=EX_NAME,
            text=EX_TEXT,
            check=EX_CHECK,
            solution=EX_SOLUTION,
            )

    def test_direct(self):
        self.assertEqual(self.ex.as_yaml(), EX_YAML)

    def test_exporting_exercise(self):
        self.login()
        response = self.client.get(reverse('yaml_exercise', args=[self.ex.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, EX_YAML)

    def test_cant_export_exercise_anonymously(self):
        url = reverse('yaml_exercise', args=[self.ex.id])
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

    def test_cant_export_others_exercise(self):
        self.login()
        url = reverse('yaml_exercise', args=[10])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_trailing_whitespace_doesnt_bother_me(self):
        # PyYaml won't write text with trailing whitespace to a literal block,
        # it wants to switch to quoted scalars instead.  We should trim the
        # trailing whitespace to keep it from freaking out.
        ex = Exercise.objects.get(slug=EX_SLUG)
        ex.check = ex.check.replace("\n", " \n")
        self.assertEqual(ex.as_yaml(), EX_YAML)


class YamlImportTest(ChoosyDjangoTestCase):

    fixtures = ['users.yaml']

    def test_importing_exercise(self):
        self.assertEqual(0, Exercise.objects.count())

        # Visit the import page
        self.login()
        response = self.client.get(reverse('import_exercise'))
        self.assertEqual(response.status_code, 200)

        # Post to the import page.
        yaml_file = StringIO.StringIO(EX_YAML)
        yaml_file.name = "test_yaml.yaml"
        response = self.client.post(reverse('import_exercise'), {'yamlfile': yaml_file}, follow=True) 

        ex = Exercise.objects.get(slug=EX_SLUG)
        self.assertEqual(ex.name, EX_NAME)
        self.assertEqual(ex.text, EX_TEXT)
        self.assertEqual(ex.check, EX_CHECK)
        self.assertEqual(ex.solution, EX_SOLUTION)

        self.assertRedirects(response, reverse('desk_show_exercise', args=[ex.id]))

    def test_importing_badly(self):
        self.login()
        response = self.client.post(reverse('import_exercise'), {}, follow=True) 
        self.assertFormError(response, 'form', None, [])
        self.assertFormError(response, 'form', 'yamlfile', ['This field is required.'])

    def test_cant_import_anonymously(self):
        # Can't visit the import page.
        url = reverse('import_exercise')
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))

        # Can't actually import.
        response = self.client.post(url, {}, follow=True) 
        self.assertRedirects(response, "%s?next=%s" % (settings.LOGIN_URL, url))
