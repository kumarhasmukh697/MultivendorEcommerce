#!/usr/bin/env bash
set -o errexit

# Install system dependencies for GDAL and PostGIS
apt-get update
apt-get install -y gdal-bin libgdal-dev libpq-dev

# Set GDAL environment variables
export GDAL_CONFIG=/usr/bin/gdal-config
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and collect static files
python manage.py migrate
python manage.py collectstatic --noinput