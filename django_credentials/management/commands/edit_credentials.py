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

    def handle(self, *args, **kwargs):
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
