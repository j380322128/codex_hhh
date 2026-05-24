"""WSGI config for codex_hhh project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codex_hhh.settings")

application = get_wsgi_application()
