import os

from django.core.management.base import BaseCommand
from pathlib import Path

from ... import credentials


class Command(BaseCommand):
    help = 'Open the credentials file for editing'

    def handle(self, *args, **kwargs):
        creds = credentials.Credentials(credentials._get_base_dir())
        creds.read()
        decrypted_filename: Path = Path(credentials._get_base_dir(), 'decrypted.ini')
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

