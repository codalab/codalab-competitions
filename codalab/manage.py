#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
<<<<<<< HEAD
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
=======
    if os.environ.get('LOCAL_CONFIGURATION_PATH'):
        sys.path.append(os.environ.get('LOCAL_CONFIGURATION_PATH'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")
>>>>>>> master
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')
    os.environ.setdefault('DJANGO_LOCAL_CONFIGURATION', 'codalab.settings.local_configuration')

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
