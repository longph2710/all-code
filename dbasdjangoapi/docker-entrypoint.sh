echo "make migrations!"
python manage.py makemigrations

echo "apply migrations!"
python manage.py migrate

echo "runserver!"
python manage.py runserver 0.0.0.0:8000