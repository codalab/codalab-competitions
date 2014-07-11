import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from apps.web import models

User = get_user_model()


class OrganizerDataSetCreateTests(TestCase):
    #requires login
    pass


class OrganizerDataSetUpdateTests(TestCase):
    #requires login
    #requires ownership of dataset
    pass


class OrganizerDataSetDeleteTests(TestCase):
    #requires login
    #requires ownership of dataset
    pass


class OrganizerDataSetListViewTests(TestCase):
    #requires login
    pass
