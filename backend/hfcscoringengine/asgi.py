#!/usr/bin/env python
"""ASGI config for hfcscoringengine project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.railway")

application = get_asgi_application()
