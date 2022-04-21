from typing import Optional
from typing import Text

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser

from env_credentials import credentials

from ...credentials import get_default_dir


class Command(BaseCommand):
    help = "Open the credentials file for editing"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--dir",
            "-d",
            type=str,
            required=False,
            default=None,
            help="The directory in which the configuration and key files are stored.",
        )
        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser("edit", help="Open the credentials file in your editor for altering.")
        subparsers.add_parser("init", help="Initialize the credentials and master key files.")
        subparsers.add_parser("show", help="Decrypt and print the credentials file to the terminal.")

    def handle_init(self, *args, **kwargs):
        credentials_dir: Optional[Text] = kwargs.get("dir") or get_default_dir()

        creds = credentials.Credentials(credentials_dir)
        creds.initialize()

    def handle_edit(self, *args, **kwargs):
        credentials_dir: Optional[Text] = kwargs.get("dir") or get_default_dir()

        creds = credentials.Credentials(credentials_dir)
        creds.edit()

    def handle_show(self, *args, **kwargs):
        credentials_dir: Optional[Text] = kwargs.get("dir") or get_default_dir()

        creds = credentials.Credentials(credentials_dir)
        self.stdout.write(creds.read_file())

    def handle(self, *args, **kwargs):
        handlers = {
            "edit": self.handle_edit,
            "init": self.handle_init,
            "show": self.handle_show,
        }

        command = kwargs.get("command")
        handler = handlers.get(command)

        if handler is None:
            print("Subcommand must be provded\n")
            self.print_help("manage.py", "credentials")
            exit(1)

        handler(*args, **kwargs)
