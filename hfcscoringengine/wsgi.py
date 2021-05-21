"""
WSGI config for hfcscoringengine project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

ROOT_DIR = Path(__file__).resolve(strict=True).parent
sys.path.append(str(ROOT_DIR / "scoringengine"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hfcscoringengine.settings.production')

application = get_wsgi_application()
