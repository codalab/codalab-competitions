from django.contrib import admin
import models
import reversion


class CompetitionAdmin(reversion.VersionAdmin):
    pass
admin.site.register(models.Competition, CompetitionAdmin)
