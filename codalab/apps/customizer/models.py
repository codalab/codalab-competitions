from django.db import models
from lxml.html.clean import clean_html


class Configuration(models.Model):
    header_logo = models.ImageField(upload_to='main_logo', null=True, blank=True)

    front_page_message = models.TextField(null=True, blank=True)

    # The competition to point the front page to, the only one the users should see
    only_competition = models.ForeignKey('web.Competition', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.front_page_message:
            self.front_page_message = clean_html(self.front_page_message)
        super(Configuration, self).save(*args, **kwargs)
