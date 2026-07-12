"""
WSGI config for luxury_realestate project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxury_realestate.settings')

application = get_wsgi_application()

# Vercel's Python runtime looks for a module-level variable named ``app``.
app = application
