#!/usr/bin/env python
"""WSGI config for hfcscoringengine project."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.test_minimal")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
