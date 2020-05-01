import os
import shutil
import tempfile

from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from env_credentials.credentials import CredentialsException
from django_credentials import credentials


class TestCredentialCommands(TestCase):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp(dir=os.path.join(os.path.dirname(__file__), 'test_fixtures'))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmpdir)

    def test_commands_default_to_settings_module(self):
        call_command('credentials', 'init')

        key_path = os.path.join(os.path.dirname(__file__), 'test_fixtures', 'master.key')
        self.assertTrue(os.path.exists(key_path))

    def test_init_creates_key_and_credentials_in_settings(self):
        out = StringIO()
        call_command('credentials', '-d', self.tmpdir, 'init', stdout=out)

        key_path = os.path.join(self.tmpdir, 'master.key')
        self.assertTrue(os.path.exists(key_path))
        credentials_path = os.path.join(self.tmpdir, 'credentials.env.enc')
        self.assertTrue(os.path.exists(credentials_path))
        ignore_file = os.path.join(self.tmpdir, '.gitignore')
        with open(ignore_file, 'r') as f:
            content = f.read()
        self.assertIn('master.key', content)

    def test_edit(self):
        out = StringIO()
        call_command('credentials', '-d', self.tmpdir, 'init')
        os.environ['EDITOR'] = 'echo "test=1" >'
        call_command('credentials', '-d', self.tmpdir, 'edit')
        call_command('credentials', '-d', self.tmpdir, 'show', stdout=out)
        content = out.getvalue()
        self.assertEqual('test=1\n', content)


class TestCredentials(TestCase):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp(dir=os.path.join(os.path.dirname(__file__), 'test_fixtures'))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmpdir)

    def test_loads_credentials(self):
        call_command('credentials', '-d', self.tmpdir, 'init')
        credentials.load(credentials_dir=self.tmpdir)
        assert os.environ.get('FIRST') == 'one'

    def test_default_dir_without_settings(self):
        with self.assertRaises(CredentialsException) as cm:
            existing_settings = os.environ['DJANGO_SETTINGS_MODULE']
            del os.environ['DJANGO_SETTINGS_MODULE']
            credentials.get_default_dir()

            e = cm.exception
            self.assertEqual(e.message, 'Unable to find the DJANGO_SETTINGS_MODULE')

            os.environ['DJANGO_SETTINGS_MODULE'] = existing_settings

    def test_default_dir_with_invalid_settings(self):
        with self.assertRaises(CredentialsException) as cm:
            existing_settings = os.environ['DJANGO_SETTINGS_MODULE']
            os.environ['DJANGO_SETTINGS_MODULE'] = 'not_real.settings'
            credentials.get_default_dir()

            e = cm.exception
            self.assertEqual(e.message, 'Unable to find the DJANGO_SETTINGS_MODULE')

            os.environ['DJANGO_SETTINGS_MODULE'] = existing_settings

