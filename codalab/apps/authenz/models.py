import re

from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class User(auth_models.AbstractUser):
    pass
