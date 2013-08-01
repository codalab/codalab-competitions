#!/usr/bin/env python

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth import get_user_model
from django.contrib.auth.management import create_superuser
from django.db.models import signals

User = get_user_model()

# From http://stackoverflow.com/questions/1466827/ --
#
# Prevent interactive question about wanting a superuser created.  (This code
# has to go in this otherwise empty "models" module so that it gets processed by
# the "syncdb" command during database creation.)
signals.post_syncdb.disconnect(
    create_superuser,
    sender=auth_models,
    dispatch_uid='django.contrib.auth.management.create_superuser')

# Create our own test user automatically.

def create_adminuser(app, created_models, verbosity, **kwargs):
  if not settings.DEBUG:
    return
  name="admin"
  email="admin@codalab.com"
  password="C0daLab$"
  try:
    User.objects.get(username=name)
  except User.DoesNotExist:
    print "*" * 80
    print "Creating admin user -- login: %s, password: %s" % (name, password)
    print "*" * 80
    admin = User(email=email, username=name)
    admin.set_password(password)
    admin.is_staff=True
    admin.is_active=True
    admin.is_superuser=True
    admin.save()
    assert admin
  else:
    print "Admin user already exists."

signals.post_syncdb.connect(create_adminuser,
    sender=auth_models, dispatch_uid='common.models.create_adminuser')

# From: http://djangosnippets.org/snippets/1875/
# #!/usr/bin/env python
# from django.conf import settings
# from django.contrib.auth import models as auth_models
# from django.contrib.auth.management import create_superuser
# from django.db.models import signals
# # From http://stackoverflow.com/questions/1466827/ --
# #
# # Prevent interactive question about wanting a superuser created.  (This code
# # has to go in this otherwise empty "models" module so that it gets processed by
# # the "syncdb" command during database creation.)
# signals.post_syncdb.disconnect(
#     create_superuser,
#     sender=auth_models,
#     dispatch_uid='django.contrib.auth.management.create_superuser')
# # Create our own test user automatically.
# def create_testuser(app, created_models, verbosity, **kwargs):
#   if not settings.DEBUG:
#     return
#   try:
#     auth_models.User.objects.get(username='test')
#   except auth_models.User.DoesNotExist:
#     print '*' * 80
#     print 'Creating test user -- login: test, password: test'
#     print '*' * 80
#     assert auth_models.User.objects.create_superuser('test', 'x@x.com', 'test')
#   else:
#     print 'Test user already exists.'
# signals.post_syncdb.connect(create_testuser,
#     sender=auth_models, dispatch_uid='common.models.create_testuser')
