#!/usr/bin/env python
"""WSGI config for hfcscoringengine project."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.production")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
