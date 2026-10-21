#!/usr/bin/env bash
# Build script for Vercel deployment
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
