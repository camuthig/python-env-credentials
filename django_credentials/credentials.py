import importlib
import os
import sys
from importlib.machinery import SourceFileLoader
from os import PathLike
from pathlib import Path
from typing import Optional
from typing import Text
from typing import Union

from env_credentials.credentials import Credentials
from env_credentials.credentials import CredentialsException


def get_default_dir() -> PathLike:
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")

    if settings_module is None:
        raise CredentialsException("Unable to find the DJANGO_SETTINGS_MODULE")

    f = importlib.find_loader(settings_module)

    if f is None:
        raise CredentialsException("Unable to find the DJANGO_SETTINGS_MODULE")

    if not isinstance(f, SourceFileLoader):
        raise CredentialsException("Invalid settings module")

    path = f.path

    if isinstance(path, bytes):
        path = path.decode(sys.getdefaultencoding())

    return Path(path).parent


def load(credentials_dir: Optional[Union[Text, PathLike]] = None):
    credentials_dir = credentials_dir or get_default_dir()
    Credentials(credentials_dir=credentials_dir).load()
