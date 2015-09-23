# This script must be run using the Python in the codalab virtualenv.
import sys
import os.path
import os

# This is a really, really long way around saying that if the script is in
# codalab\scripts\users.py, we need to add, ../../../codalab to the
# sys.path to find the settings
root_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
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
    print >>out, '\t'.join(map(str, [x.id, x.username, x.email, x.date_joined, x.last_login]))
