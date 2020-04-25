# Env Credentials

Manage environment variables use the dotenv pattern with encrypted files.

This project is an attempted port of the [credentials pattern](https://edgeguides.rubyonrails.org/security.html#custom-credentials)
found in Ruby on Rails.

## Installation

Using pip:

```bash
pip install env-credentials[django]
```

Using poetry:

```bash
poetry add env-credentials[django]
```

## Usage

Initializing and editing the encrypted credentials file is only supported with Django at this time. Additional CLI
tooling can be built for framework-less projects or projects using other frameworks.

### Django

After adding the dependency to your project, add the Django app

```python
INSTALLED_APPS = [
    # ...
    'django_credentials',
    # ...
]
```

You can then initialize the credentials files with

```bash
./manage.py init_credentials
```

This will create a two new files called `master.key` and `credentials.env.enc` in your root folder. If a `.gitignore`
file exists in the same directory, it will also add `master.key` to it.

**Be sure to ignore your master.key file if the gitignore file cannot be automatically updated.**

You can then edit the values in the file using

```bash
./manage.py edit_credentials
```

Be sure that your `$EDITOR` environment variable is set, as that is what the decrypted file will be opened with.

Finally, to load the values into your environment, you should add the following code to your `wsgi.py` and `manage.py`
files

```python
from env_credentials.credentials import Credentials

Credentials().load()
```
