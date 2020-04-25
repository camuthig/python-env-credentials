import inspect
import os
import secrets
import sys

from configparser import ConfigParser
from configparser import ExtendedInterpolation
from dotenv import dotenv_values, load_dotenv
from io import StringIO
from typing import Dict
from typing import Optional
from typing import Text

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Credentials:
    key: AESGCM
    nonce: bytes

    _key_filename = 'master.key'
    _config_filename = 'credentials.env.enc'

    _content: Optional[str] = None
    _values: Optional[Dict] = None
    _loaded: bool = False

    def __init__(self, credentials_dir):
        self.credentials_dir = credentials_dir

    @staticmethod
    def initialize(credentials_dir=None) -> 'Credentials':
        instance = Credentials(credentials_dir)
        instance._generate_key()
        instance._generate_file()
        return instance

    def _read(self) -> str:
        if self._content:
            return self._content

        if not hasattr(self, 'key') or not hasattr(self, 'nonce') or not self.key or not self.nonce:
            self.key, self.nonce = self._get_key()

        with open(self.get_config_path()) as f:
            encrypted = f.read()

        self._content =  self.key.decrypt(self.nonce, bytes.fromhex(encrypted), None).decode('utf-8')

        return self._content

    def values(self) -> Dict[Text, Optional[Text]]:
        if not self._values:
            self._values = dotenv_values(stream=StringIO(self._read()))

        return self._values

    def load(self):
        if self._loaded:
            return

        load_dotenv(StringIO(self._read()))
        self._loaded = True

    def _generate_key(self):
        full_file_path = os.path.join(self.credentials_dir, self._key_filename)

        if os.path.exists(full_file_path):
            print('Key already exists')
            key, nonce = self._get_key()
            return full_file_path, key, nonce

        key = AESGCM.generate_key(128)
        nonce = secrets.token_hex(12)
        with open(full_file_path, 'w') as f:
            f.write(f'{key.hex()}.{nonce}')

        self.key = AESGCM(key)
        self.nonce = bytes.fromhex(nonce)

    def _generate_file(self):
        sample_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example.env')
        with open(sample_path) as s:
            txt = s.read()
            encrypted_path = os.path.join(self.credentials_dir, self._config_filename)
            if os.path.exists(encrypted_path):
                print('Credentials file already exists')
                return

            self.write_file(txt)

    def _get_key(self) -> (AESGCM, bytes):
        key = None
        with open(os.path.join(self.credentials_dir, self._key_filename)) as f:
            key = f.read()

        key, nonce = key.split('.', 2)

        return AESGCM(bytes.fromhex(key)), bytes.fromhex(nonce)

    def get_key_path(self):
        return os.path.join(self.credentials_dir, self._key_filename)

    def get_config_path(self):
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