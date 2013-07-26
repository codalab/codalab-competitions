from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.core.mail import send_mail
import re

class ThisUserManager(UserManager):

    def create_user(self, email, password=None, username=None, affiliation=None,  **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            username = email
        now=timezone.now()
        email = UserManager.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

class User(AbstractBaseUser):
    username = models.CharField(_('username'), max_length=100, unique=True,
        help_text=_('Required. 100 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w\d.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    email = models.EmailField(_('email address'), unique=True)

    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    affiliation = models.CharField(_('affiliation'), max_length=100, blank=True)
    home_page = models.URLField(_('home page'), null=True, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_superuser = models.BooleanField(default=False)

    objects = ThisUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"     
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
