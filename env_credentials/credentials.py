import os
import re
import secrets

from dotenv import dotenv_values, load_dotenv
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Text
from typing import Tuple
from typing import Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CredentialsException(Exception):
    message: str

    def __init__(self, message: Optional[str] = None):
        self.message = message or 'Error loading credentials'

    def __str__(self):
        return self.message


class DirectoryNotFoundException(CredentialsException):
    def __init__(self, directory: Union[Text, PathLike]):
        self.message = f'Could not find credentials directory {directory}'


class KeyNotFoundException(CredentialsException):
    def __init__(self, file: Union[Text, PathLike]):
        self.message = f'Could not find key file: {file}'


class CredentialsNotFoundException(CredentialsException):
    def __init__(self, file: Union[Text, PathLike]):
        self.message = f'Could not find credentials file {file}'


class InvalidKeyException(CredentialsException):
    def __init__(self, previous):
        self.message = f'The found key was invalid {previous}'
        self.previous = previous


class Credentials:
    key: AESGCM
    nonce: bytes

    _key_filename = 'master.key'
    _config_filename = 'credentials.env.enc'

    _content: Optional[str] = None
    _values: Optional[Dict] = None
    _loaded: bool = False

    def __init__(self, credentials_dir: Union[Text, PathLike]):
        if not Path(credentials_dir).exists():
            raise DirectoryNotFoundException(credentials_dir)

        self.credentials_dir = credentials_dir

    def initialize(self):
        self._generate_key()
        self._generate_file()

    def _read(self) -> str:
        if self._content:
            return self._content

        if not hasattr(self, 'key') or not hasattr(self, 'nonce') or not self.key or not self.nonce:
            self.key, self.nonce = self._get_key()

        path = Path(self.get_config_path())

        if not path.exists():
            raise CredentialsNotFoundException(path)

        with open(path) as f:
            encrypted = f.read()

        self._content = self.key.decrypt(self.nonce, bytes.fromhex(encrypted), None).decode('utf-8')

        return self._content

    def values(self) -> Dict[Text, Optional[Text]]:
        if not self._values:
            self._values = dotenv_values(stream=StringIO(self._read()))

        return self._values

    def load(self) -> None:
        if self._loaded:
            return

        load_dotenv(stream=StringIO(self._read()))
        self._loaded = True

    def _ignore_key(self, key_path):
        ignore_file = os.path.join(self.credentials_dir, '.gitignore')

        rel_path = os.path.relpath(key_path, self.credentials_dir)

        if os.path.exists(ignore_file):
            with open(ignore_file, 'r') as f:
                content = f.read()

            search = re.search(f'^{re.escape(rel_path)}$', content, re.MULTILINE)
            if not search:
                with open(ignore_file, 'a') as f:
                    f.write(f'\n{rel_path}')
                    return
        else:
            with open(ignore_file, 'a') as f:
                f.write(rel_path)

    def _generate_key(self):
        full_file_path = os.path.join(self.credentials_dir, self._key_filename)

        if os.path.exists(full_file_path):
            key, nonce = self._get_key()
            return full_file_path, key, nonce

        key = AESGCM.generate_key(128)
        nonce = secrets.token_hex(12)
        with open(full_file_path, 'w') as f:
            f.write(f'{key.hex()}.{nonce}')

        self.key = AESGCM(key)
        self.nonce = bytes.fromhex(nonce)

        self._ignore_key(full_file_path)

    def _generate_file(self):
        sample_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example.env')
        with open(sample_path) as s:
            txt = s.read()
            encrypted_path = os.path.join(self.credentials_dir, self._config_filename)
            if os.path.exists(encrypted_path):
                return

            self.write_file(txt)

    def _get_key(self) -> Tuple[AESGCM, bytes]:
        key = None
        path = Path(self.credentials_dir, self._key_filename)

        if not path.exists():
            raise KeyNotFoundException(path)

        with open(path) as f:
            key = f.read()

        try:
            key, nonce = key.split('.', 2)

            return AESGCM(bytes.fromhex(key)), bytes.fromhex(nonce)
        except ValueError as e:
            raise InvalidKeyException(e)

    def get_key_path(self) -> str:
        return os.path.join(self.credentials_dir, self._key_filename)

    def get_config_path(self) -> str:
        return os.path.join(self.credentials_dir, self._config_filename)

    def read_file(self) -> str:
        return self._read()

    def write_file(self, data):
        with open(self.get_config_path(), 'w') as e:
            e.write(self.key.encrypt(
                self.nonce,
                bytes(data, 'utf-8'),
                None,
            ).hex())

    def edit(self):
        decrypted_filename = Path(self.credentials_dir, 'decrypted.ini')
        try:
            with open(decrypted_filename, 'w') as f:
                f.write(self.read_file())

            os.system(f'{os.getenv("EDITOR")} {decrypted_filename}')

            with open(decrypted_filename, 'r') as f:
                txt = f.read()
                self.write_file(txt)

            self.clear()

        finally:
            if decrypted_filename.is_file():
                os.remove(decrypted_filename)

    def clear(self):
        self._content = None
        self._values = None
        self._loaded = None
