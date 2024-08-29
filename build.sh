# echo "Building the project..."
# python 3.12 -m pip install -r requirements.txt

# echo "Make Migration..."
# python 3.12 manage.py makemigrations --noinput
# python 3.12 manage.py migrate --noinput

# echo "Collect Static..."
# python 3.12 manage.py collectstatic --noinput --clear


echo "Building the project..."
python 3.12.5 -m pip install -r requirements.txt

echo "Make Migration..."
python 3.12.5 manage.py makemigrations --noinput
python 3.12.5 manage.py migrate --noinput

echo "Collect Static..."
python 3.12.5 manage.py collectstatic --noinput --clear

