# This script must be run using the Python in the codalab virtualenv.
import sys
import os.path
import os

# Find the root codalab directory and add it to the settings.
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

# Import the user model
from django.contrib.auth import get_user_model
User = get_user_model()

# Print out users.
for x in User.objects.all():
    print '\t'.join(map(str, [x.id, x.username, x.email, x.date_joined, x.last_login]))
