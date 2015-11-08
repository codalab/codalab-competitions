import json
import os
import os.path
import sys

# CodaLab website supplies an OAuth server.
# This script takes in a config.json file for the bundle service and
# substitutes the proper OAuth information.

root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

from configurations import importer
importer.install()

from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.all()[0]

from oauth2_provider.models import Application

client, created = Application.objects.get_or_create(
                    user=user,
                    client_type=Application.CLIENT_CONFIDENTIAL,
                    authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
                    name='Bundle service client')

if len(sys.argv) != 2:
    print 'Usage: %s <bundle service config json file>' % sys.argv[0]
    sys.exit(1)
json_path = sys.argv[1]

cfg = json.loads(open(json_path).read())
auth = cfg['server']['auth']
auth['app_id'] = client.client_id
auth['app_key'] = client.client_secret
print json.dumps(cfg, sort_keys=True, indent=4, separators=(',', ': '))
