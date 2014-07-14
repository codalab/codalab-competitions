import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.web import models

User = get_user_model()


class OrganizerDataSetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="organizer", password="pass")
        self.other_user = User.objects.create_user(username="potentially_malicious", password="pass")
        self.dataset = models.OrganizerDataSet.objects.create(
            name="Test",
            type="None",
            data_file=SimpleUploadedFile("something.txt", "contents of file"),
            uploaded_by=self.user
        )


#class OrganizerDataSetModelTestsCase(OrganizerDataSetTestCase):
#    def test_save_generates_key_with_file_name_and_uuid(self):
#        # self.dataset was already saved above
#        file_name = "something.txt"
#        uuid4_length = 36
#        self.assertEquals(self.dataset.key[:len(file_name)], file_name)
#        self.assertEquals(len(self.dataset.key), len(file_name) + uuid4_length)
#
#    def test_save_generates_key_with_filename_greather_than_64_chars(self):
#        file_name = "something.txt"*10
#        file_name = file_name[:60] # it's too long, crashes database
#        self.dataset = models.OrganizerDataSet.objects.create(
#            name="Test",
#            type="None",
#            data_file=SimpleUploadedFile(file_name, "contents of file"),
#            uploaded_by=self.user
#        )
#        max_file_name_length = 64
#        uuid4_length = 36
#        self.assertEquals(self.dataset.key[:max_file_name_length], file_name[:max_file_name_length])
#        self.assertEquals(len(self.dataset.key), max_file_name_length + uuid4_length)


class OrganizerDataSetCreateTestsCase(OrganizerDataSetTestCase):
    def test_dataset_creation_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_create"))
        self.assertEquals(resp.status_code, 302)


class OrganizerDataSetUpdateTestsCase(OrganizerDataSetTestCase):
    def test_dataset_update_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_update", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 302)

    def test_dataset_update_returns_404_when_not_dataset_owner(self):
        self.client.login(username="potentially_malicious", password="pass")
        resp = self.client.get(reverse("my_datasets_update", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 404)

    def test_dataset_update_returns_200_when_owner(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.get(reverse("my_datasets_update", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 200)


class OrganizerDataSetDeleteTestsCase(OrganizerDataSetTestCase):
    def test_dataset_delete_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets_delete", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 302)

    def test_dataset_delete_returns_404_when_not_dataset_owner(self):
        self.client.login(username="potentially_malicious", password="pass")
        resp = self.client.get(reverse("my_datasets_delete", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 404)

    def test_dataset_delete_returns_200_when_owner(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.get(reverse("my_datasets_delete", kwargs={"pk": self.dataset.pk}))
        self.assertEquals(resp.status_code, 200)


class OrganizerDataSetListViewTestsCase(OrganizerDataSetTestCase):
    def test_dataset_list_view_returns_302_when_not_logged_in(self):
        resp = self.client.get(reverse("my_datasets"))
        self.assertEquals(resp.status_code, 302)
