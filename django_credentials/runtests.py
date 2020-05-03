#!/usr/bin/env python
import atexit
import os
import sys
import shutil
import django

from django.conf import settings
from django.core.management import call_command


def runtests():
    # create a temporary directory sturcture for the "project"
    # Create a specific subdirectory for the duration of the test suite.
    test_fixtures_dir = os.path.join(os.path.dirname(__file__), 'test_fixtures')
    os.mkdir(test_fixtures_dir)
    open(os.path.join(test_fixtures_dir, '__init__.py'), 'a').close()
    atexit.register(shutil.rmtree, test_fixtures_dir)

    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_credentials.test_fixtures')
        # Choose database for settings
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        }

        # Configure test environment
        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=(
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django.contrib.sites',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',

                'django_credentials',
            ),
            ROOT_URLCONF='',  # tests override urlconf, but it still needs to be defined
            MIDDLEWARE_CLASSES=(
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ],
        )

    if django.VERSION >= (1, 7):
        django.setup()
    failures = call_command(
        'test', 'django_credentials', interactive=False, failfast=False, verbosity=2)

    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
