import inspect
import os
import secrets
import sys

from configparser import ConfigParser
from configparser import ExtendedInterpolation
from typing import Dict
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# WIP this function probably belongs somewhere focused on Django
def _get_base_dir():
    frame = inspect.currentframe()
    for i in range(20):
        if frame is None:
            print('Unable to find the base directory of the project')
            # WIP better error handling
            exit(1)

        file_name = os.path.basename(frame.f_code.co_filename)
        if file_name == 'manage.py':
            return os.path.abspath(os.path.dirname(file_name))

        frame = frame.f_back


def get_key_path(file_path, filename):
    return os.path.join(file_path, filename)


def get_file_path(file_path, filename):
    return os.path.join(file_path, filename)


def get_key_from_path(file_path, filename):
    key = None
    with open(os.path.join(file_path, filename)) as f:
        key = f.read()

    key, nonce = key.split('.', 2)

    return AESGCM(bytes.fromhex(key)), bytes.fromhex(nonce)


def get_key(path=None):
    return get_key_from_path(get_key_path(path))

class Credentials:
    key: AESGCM
    nonce: bytes

    _key_filename = 'master.key'
    _config_filename = 'credentials.ini.enc'

    _config: Optional[ConfigParser] = None

    def __init__(self, credentials_dir=None):
        self.credentials_dir = credentials_dir or _get_base_dir()

    @staticmethod
    def initialize(credentials_dir=None) -> 'Credentials':
        instance = Credentials(credentials_dir)
        instance._generate_key()
        instance._generate_file()
        return instance

    def read(self):
        self.key, self.nonce = self._get_key()
        self._config = self._parse_config()

    def _generate_key(self):
        full_file_path = get_key_path(self.credentials_dir, self._key_filename)

        if os.path.exists(full_file_path):
            print('Key already exists')
            key, nonce = get_key_from_path(self.credentials_dir, self._key_filename)
            return full_file_path, key, nonce

        key = AESGCM.generate_key(128)
        nonce = secrets.token_hex(12)
        with open(full_file_path, 'w') as f:
            f.write(f'{key.hex()}.{nonce}')

        self.key = AESGCM(key)
        self.nonce = bytes.fromhex(nonce)

    def _generate_file(self):
        sample_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example.txt')
        with open(sample_path) as s:
            txt = s.read()
            encrypted_path = get_file_path(self.credentials_dir, self._config_filename)
            if os.path.exists(encrypted_path):
                print('Credentials file already exists')
                return

            self.write_file(txt)
        
    def _get_key(self) -> (AESGCM, bytes):
        return get_key_from_path(self.credentials_dir, self._key_filename)

    def _parse_config(self) -> ConfigParser:
        decrypted = self.read_file()
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read_string(decrypted)
        return config

    def get_key_path(self):
        return os.path.join(self.credentials_dir, self._key_filename)

    def get_config_path(self):
        return os.path.join(self.credentials_dir, self._config_filename)


    def get(self, key: str, default=None): 
        return self._config['credentials'].get(key, default)

    def read_file(self):
        with open(self.get_config_path()) as f:
            encrypted = f.read()
        return self.key.decrypt(self.nonce, bytes.fromhex(encrypted), None).decode('utf-8')

    def write_file(self, data):
        with open(self.get_config_path(), 'w') as e:
            e.write(self.key.encrypt(
                self.nonce,
                bytes(data, 'utf-8'),
                None,
            ).hex())