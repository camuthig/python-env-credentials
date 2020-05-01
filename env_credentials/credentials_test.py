import io
import os
import pytest
import sys

from pathlib import Path
from tempfile import TemporaryDirectory

from .credentials import Credentials
from .credentials import DirectoryNotFoundException
from .credentials import KeyNotFoundException
from .credentials import CredentialsNotFoundException
from .credentials import InvalidKeyException


@pytest.fixture
def credentials_dir():
    with TemporaryDirectory() as dir:
        yield dir


def test_init_fails_on_missing_directory():
    with pytest.raises(DirectoryNotFoundException):
        Credentials(Path(Path(__file__).parent, 'non_existing_dir'))


def test_init_allows_string_or_path(credentials_dir: str):
    Credentials(credentials_dir)
    Credentials(Path(credentials_dir))


def test_initialize_creates_files(credentials_dir: str):
    creds = Credentials(credentials_dir)

    key_path = Path(credentials_dir, 'master.key')
    credentials_path = Path(credentials_dir, 'credentials.env.enc')

    assert not key_path.exists()
    assert not credentials_path.exists()

    creds.initialize()

    assert key_path.exists()
    assert credentials_path.exists()

    values = creds.values()

    assert 'one' == values.get('FIRST')


def test_initialization_does_nothing_if_files_exist(credentials_dir: str):
    creds = Credentials(credentials_dir)

    key_path = Path(credentials_dir, 'master.key')
    credentials_path = Path(credentials_dir, 'credentials.env.enc')

    creds.initialize()

    with open(key_path, 'r') as f:
        initialized_key = f.read()

    with open(credentials_path, 'r') as f:
        initialized_credentials = f.read()

    new_creds = Credentials(credentials_dir)

    new_creds.initialize()

    with open(key_path, 'r') as f:
        assert initialized_key == f.read()

    with open(credentials_path, 'r') as f:
        assert initialized_credentials == f.read()


def test_initialize_creates_ignore_file(credentials_dir: str):
    ignore_path = os.path.join(credentials_dir, '.gitignore')

    creds = Credentials(credentials_dir)

    creds.initialize()

    with open(ignore_path, 'r') as f:
        assert f.read() == 'master.key'


def test_initialize_updates_ignore_file(credentials_dir: str):
    ignore_path = os.path.join(credentials_dir, '.gitignore')
    open(ignore_path, 'w').close()

    creds = Credentials(credentials_dir)

    creds.initialize()

    with open(ignore_path, 'r') as f:
        assert f.read() == '\nmaster.key'


def test_initialize_does_not_update_ignore_file_if_already_set(credentials_dir: str):
    ignore_path = os.path.join(credentials_dir, '.gitignore')
    with open(ignore_path, 'w') as f:
        f.write('stuff\nmaster.key')

    creds = Credentials(credentials_dir)

    creds.initialize()

    with open(ignore_path, 'r') as f:
        assert f.read() == 'stuff\nmaster.key'


def test_load_key_not_found_returns_helpful_error(credentials_dir: str):
    creds = Credentials(credentials_dir)

    creds.initialize()

    os.remove(creds.get_key_path())

    reloaded_creds = Credentials(credentials_dir)

    with pytest.raises(KeyNotFoundException):
        reloaded_creds.load()


def test_load_credentials_not_found_returns_helpful_error(credentials_dir: str):
    creds = Credentials(credentials_dir)

    creds.initialize()

    os.remove(creds.get_config_path())

    reloaded_creds = Credentials(credentials_dir)

    with pytest.raises(CredentialsNotFoundException):
        reloaded_creds.load()


def test_load_invalid_key_returns_helpful_error(credentials_dir: str):
    creds = Credentials(credentials_dir)

    creds.initialize()

    with open(creds.get_key_path(), 'w') as f:
        f.write('test')

    reloaded_creds = Credentials(credentials_dir)

    with pytest.raises(InvalidKeyException):
        reloaded_creds.load()


def test_uses_cached_values(credentials_dir: str):
    creds = Credentials(credentials_dir)

    creds.initialize()

    creds.load()
    creds.values()

    os.remove(creds.get_config_path())

    creds.load()
    creds.values()

    reloaded_creds = Credentials(credentials_dir)

    with pytest.raises(CredentialsNotFoundException):
        reloaded_creds.load()


def test_edits_file_based_on_editor(credentials_dir: str):
    creds = Credentials(credentials_dir)

    creds.initialize()

    os.environ['EDITOR'] = 'echo "test=1" >'
    creds.edit()

    assert creds.values() == {'test': '1'}
