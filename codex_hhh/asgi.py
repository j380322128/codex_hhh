"""ASGI config for codex_hhh project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codex_hhh.settings")

application = get_asgi_application()
