from django.contrib import admin
import models

class CompetitionAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Competition, CompetitionAdmin)

class CompetitionInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.CompetitionInfo, CompetitionInfoAdmin)
