from django.test import TestCase

from apps.authenz.models import ClUser
from apps.web.utils import clean_html_script


class HTMLCleanTestCase(TestCase):

    def setUp(self):
        self.user = ClUser.objects.create_user(username="organizer", password="pass")

    def test_script_tags_get_removed_from_html_content(self):
        self.assertEquals(clean_html_script("<script></script>"), "")
        self.assertEquals(clean_html_script("<script src=\"https://www.googleorsomething\"></script>"), "")
        self.assertEquals(clean_html_script("<script src=\"https://www.googleorsomething\">There's some stuff in between here too </script>"), "")
        self.assertEquals(clean_html_script("<script src=\"https://www.googleorsomething\">There's some stuff in between here too </script>There should be some stuff here."), "There should be some stuff here.")
        self.assertEquals(clean_html_script("<b>A strong word</b>"), "<b>A strong word</b>")
        self.assertEquals(clean_html_script({
            'my_key': 1,
            'my_value': "twenty_seven",
        }), "{'my_value': 'twenty_seven', 'my_key': 1}")
        self.assertEquals(clean_html_script(1), "1")
