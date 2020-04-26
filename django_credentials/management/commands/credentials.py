import inspect
import os

from django.core.management.base import BaseCommand, CommandParser
from pathlib import Path
from typing import Optional
from typing import Text

from env_credentials import credentials

from ...credentials import get_default_dir


class Command(BaseCommand):
    help = 'Open the credentials file for editing'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--dir', '-d',
            type=str,
            required=False,
            default=None,
            help='The directory in which the configuration and key files are stored.',
        )
        subparsers = parser.add_subparsers(dest='command')

        subparsers.add_parser('edit', help='Open the credentials file in your editor for altering.')
        subparsers.add_parser('init', help='Initialize the credentials and master key files.')

    def get_root_dir(self) -> Optional[str]:
        frame = inspect.currentframe()

        if frame is None:
            raise Exception('Python version does not support frame inspection.' +
                            'Please specify credentials directory instead.')

        for i in range(20):
            if frame is None:
                raise Exception('Unable to find base directory of the project')

            file_name = os.path.basename(frame.f_code.co_filename)
            if file_name == 'manage.py':
                return os.path.abspath(os.path.dirname(file_name))

            frame = frame.f_back

        return None

    def _ignore_key(self, key_file):
        root_dir = self.get_root_dir()

        if root_dir is None:
            raise Exception('Unable to find base directory of the project')

        ignore_file = os.path.join(root_dir, '.gitignore')

        if os.path.exists(ignore_file):
            with open(ignore_file, 'a') as f:
                rel_path = os.path.relpath(key_file, os.path.dirname(ignore_file))
                f.write(f'\n{rel_path}')
        else:
            print(f'Git ignore file not found at {ignore_file}. ' +
                  'Be sure at add the key file to your gitignore wherever it is')

    def handle_init(self, *args, **kwargs):
        credentials_dir: Optional[Text] = kwargs.get('dir') or get_default_dir()

        creds = credentials.Credentials.initialize(credentials_dir)
        self._ignore_key(creds.get_key_path())

    def handle_edit(self, *args, **kwargs):
        credentials_dir: Optional[Text] = kwargs.get('dir') or get_default_dir()

        creds = credentials.Credentials(credentials_dir)
        decrypted_filename = Path(get_default_dir(), 'decrypted.ini')

        try:
            with open(decrypted_filename, 'w') as f:
                f.write(creds.read_file())

            os.system(f'{os.getenv("EDITOR")} {decrypted_filename}')

            with open(decrypted_filename, 'r') as f:
                txt = f.read()
                creds.write_file(txt)

        finally:
            if decrypted_filename.is_file():
                os.remove(decrypted_filename)

    def handle(self, *args, **kwargs):
        handlers = {
            'edit': self.handle_edit,
            'init': self.handle_init,
        }

        command = kwargs.get('command')
        handler = handlers.get(command)

        if handler is None:
            print('Subcommand must be provded\n')
            self.print_help('manage.py', 'credentials')
            exit(1)

        handler(*args, **kwargs)
