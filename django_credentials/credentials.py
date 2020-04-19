import inspect
import os
import secrets
import sys

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

    def __init__(self, credentials_dir=None):
        self.credentials_dir = credentials_dir or _get_base_dir()

    @staticmethod
    def _generate_key(file_path, filename):
        full_file_path = get_key_path(file_path, filename)

        if os.path.exists(full_file_path):
            print('Key already exists')
            key, nonce = get_key_from_path(file_path, filename)
            return full_file_path, key, nonce

        key = AESGCM.generate_key(128).hex()
        nonce = secrets.token_hex(12)
        with open(file_path, 'w') as f:
            f.write(f'{key}.{nonce}')

        return file_path, key, nonce

    @staticmethod
    def _generate_file(credentials_dir, key_filename, config_filename):
        sample_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example.txt')
        with open(sample_path) as s:
            txt = s.read()
            encrypted_path = get_file_path(credentials_dir, config_filename)
            if os.path.exists(encrypted_path):
                print('Credentials file already exists')
                return
            with open(encrypted_path, 'w') as e:
                crypto, nonce = get_key_from_path(credentials_dir, key_filename)
                e.write(crypto.encrypt(
                    nonce,
                    bytes(txt, 'utf-8'),
                    None,
                ).hex())

    def get_key_path(self):
        return os.path.join(self.credentials_dir, self._key_filename)

    def get_config_path(self):
        return os.path.join(self.credentials_dir, self._config_filename)

    @classmethod
    def initialize(cls, credentials_dir=None):
        cls._generate_key(credentials_dir, cls._key_filename)
        cls._generate_file(credentials_dir, cls._key_filename, cls._config_filename)
        return Credentials(credentials_dir)

