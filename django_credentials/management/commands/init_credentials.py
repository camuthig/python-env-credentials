import os

from django.core.management.base import BaseCommand

from credentials.credentials import Credentials

from ...lib import get_base_dir


class Command(BaseCommand):
    help = 'Initialize the credentials file'

    def _ignore_key(self, key_file):
        # WIP Consider if this is the best place for this
        ignore_file = os.path.join(get_base_dir(), '.gitignore')

        if os.path.exists(ignore_file):
            with open(ignore_file, 'a') as f:
                rel_path = os.path.relpath(key_file, os.path.dirname(ignore_file))
                f.write(f'\n{rel_path}')
        else:
            print(f'Git ignore file not found at {ignore_file}. ' +
                  'Be sure at add the key file to your gitignore wherever it is')

    def handle(self, *args, **kwargs):
        creds = Credentials.initialize(get_base_dir())
        self._ignore_key(creds.get_key_path())
