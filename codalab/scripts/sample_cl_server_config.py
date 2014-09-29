import json
import os
import os.path
import sys

root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

from configurations import importer
importer.install()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'codalab'

print 'Checking that confidential client exists for user %s\n' % username
user = User.objects.get(username=username)

from oauth2_provider.models import Application

client, created = Application.objects.get_or_create(
                    user=user,
                    client_type=Application.CLIENT_CONFIDENTIAL,
                    authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
                    name='Bundle service client')

if created:
    print 'Created new OAuth client:'
    print '  Client id: %s' % client.client_id
    print '  Client secret: %s' % client.client_secret
else:
    print 'Client already exists.'

print '\nAdd the following server block to your CLI config:\n'
cfg = { 'class': 'SQLiteModel',
        'host': 'localhost',
        'port': 2800,
        'auth': {
            'class': 'OAuthHandler',
            'address': 'http://localhost:8000',
            'app_id': client.client_id,
            'app_key': client.client_secret
        } 
      }
print '"server": %s\n' % json.dumps(cfg, sort_keys=True, indent=4, separators=(',', ': '))
