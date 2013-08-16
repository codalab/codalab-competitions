call .\config\generated\startup_env.bat
python manage.py celery worker -P solo %*
