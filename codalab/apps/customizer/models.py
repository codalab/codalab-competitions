from django.db import models


class Configuration(models.Model):
    header_logo = models.ImageField(upload_to='main_logo', null=True, blank=True)

    # The competition to point the front page to, the only one the users should see
    only_competition = models.ForeignKey('web.Competition', null=True, blank=True)
