#!/usr/bin/env python3

import time

from subprocess import call


dump_name = time.strftime("%Y-%m-%d_%H:%M:%S.dump")

print("Making dump {}".format(dump_name))

# Make dump
call([
    'docker',
    'exec',
    'postgres',
    'bash',
    '-c',
    'PGPASSWORD=$DB_PASSWORD pg_dump -Fc -U $DB_USER $DB_NAME > /app/backups/{}'.format(
        dump_name
    )
])

# Push/destroy dump
call([
    'docker', 'exec', 'django', 'python', 'manage.py', 'upload_backup', '{}'.format(dump_name)
])
