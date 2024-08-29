# echo "Building the project..."
# python 3.12 -m pip install -r requirements.txt

# echo "Make Migration..."
# python 3.12 manage.py makemigrations --noinput
# python 3.12 manage.py migrate --noinput

# echo "Collect Static..."
# python 3.12 manage.py collectstatic --noinput --clear


#!/bin/bash

echo "Installing Python..."
apt-get update
apt-get install -y python3 python3-pip

echo "Make Migration..."
python3 manage.py makemigrations

echo "Apply Migrations..."
python3 manage.py migrate

echo "Collect Static..."
python3 manage.py collectstatic --noinput
