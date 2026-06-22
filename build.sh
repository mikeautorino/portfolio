#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip (optional, can help with dependency issues)
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a Django superuser non-interactively, if environment variable is set
if [ "$CREATE_SUPERUSER" = "True" ]; then
  python manage.py createsuperuser --no-input
fi

# Collect static files
python manage.py collectstatic --no-input
