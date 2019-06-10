import logging

from settings.components.common import (
    INSTALLED_APPS,
    MIDDLEWARE,
    config,
)


DEBUG = True

ALLOWED_HOSTS = [
    config('DOMAIN_NAME'),
    'localhost',
    '127.0.0.1',
    '[::1]',
]

STATICFILES_DIRS = []

INSTALLED_APPS += ()
MIDDLEWARE += ()
