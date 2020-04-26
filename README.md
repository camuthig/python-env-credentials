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
poetry add env-credentials --extras django
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

This will create a two new files called `master.key` and `credentials.env.enc`. It will  default to adding these files
to the same folder as where you attempted to load the values in the same folder as you loaded the values. If following
these directions, then that will be in the same folder as your `settings.py` file.

This will also attempt to add `master.key` to the `.gitignore` file colocated with your `manage.py` file, if it exists.

**Be sure to ignore your master.key file if the gitignore file cannot be automatically updated.**

Finally, add the following code to your `settings.py` file to load the credentials into `os.environ`

```python
from django_credentials import credentials

credentials.load()
```

You can then edit the values in the file using

```bash
./manage.py edit_credentials
```

**Custom Credentials Directory**

You can put your credentials files, both key and configuration, into a different directory, but must tell the library
where they are.

```python
import os

from django_credentials import credentials
from pathlib import Path

current_dir = os.path.dirname(__file__)
credentials.load(credentials_dir=Path(current_dir, credentials_dir))
```

When initializing and editing the credentials from the CLI, you can pass the `dir` option

```bash
./manage.py init_credentials -d <path>
./manage.py edit_credentials -d <path>
```
