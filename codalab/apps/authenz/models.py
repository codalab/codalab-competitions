from django.db import models
from django.contrib.auth.models import AbstractBaseUser,  AbstractUser, UserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.core.mail import send_mail
import re


class User(AbstractUser):
    pass
