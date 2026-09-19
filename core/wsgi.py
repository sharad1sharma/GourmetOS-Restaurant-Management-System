"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

# pyrefly: ignore [missing-import]
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Ensure database tables exist in serverless environment
try:
    from django.core.management import call_command
    from menu.models import Category
    if not Category.objects.exists():
        call_command('migrate', interactive=False)
        call_command('seed_data')
except Exception:
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        call_command('seed_data')
    except Exception as exc:
        print("Auto-migrate notice:", exc)

app = application
