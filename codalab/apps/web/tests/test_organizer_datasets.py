import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.web import models

User = get_user_model()


class OrganizerDataSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="organizer", password="pass")
        self.other_user = User.objects.create_user(username="potentially_malicious", password="pass")
        self.dataset = models.OrganizerDataSet.objects.create(
            name="Test",
            type="None",
            data_file=SimpleUploadedFile("something.txt", "contents of file"),
            uploaded_by=self.user
        )


class OrganizerDataSetCreateTests(OrganizerDataSetTest):
    def test_dataset_creation_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_create"))
        self.assertEquals(resp.status_code, 302)


class OrganizerDataSetUpdateTests(OrganizerDataSetTest):
    def test_dataset_update_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_update", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 302)

    def test_dataset_update_returns_404_when_not_dataset_owner(self):
        self.client.login(username="potentially_malicious", password="pass")
        resp = self.client.get(reverse("my_datasets_update", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 404)


class OrganizerDataSetDeleteTests(OrganizerDataSetTest):
    def test_dataset_delete_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_delete", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 302)

    def test_dataset_delete_returns_404_when_not_dataset_owner(self):
        self.client.login(username="potentially_malicious", password="pass")
        resp = self.client.get(reverse("my_datasets_delete", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 404)


class OrganizerDataSetListViewTests(OrganizerDataSetTest):
    def test_dataset_list_view_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets"))
        self.assertEquals(resp.status_code, 302)
