from django.contrib import admin
import models


class ExternalFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ExternalFile, ExternalFileAdmin)

class ExternalFileTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ExternalFileType, ExternalFileTypeAdmin)

class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.CompetitionDataset, DatasetAdmin)

class PhaseInlineAdmin(admin.TabularInline):
    model = models.CompetitionPhase
class DatasetInlineAdmin(admin.TabularInline):
    model = models.CompetitionDataset


class CompetitionAdmin(admin.ModelAdmin):
    inlines = [PhaseInlineAdmin,
               DatasetInlineAdmin
               ]               
admin.site.register(models.Competition, CompetitionAdmin)



class CompetitionPhaseAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.CompetitionPhase, CompetitionPhaseAdmin)

class ParticipantStatusAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ParticipantStatus, ParticipantStatusAdmin)


class ContentContainerTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ContentContainerType, ContentContainerTypeAdmin)

class ContentContainerAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ContentContainer, ContentContainerAdmin)

class ContentVisibilityAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ContentVisibility, ContentVisibilityAdmin)

class ContentEntityAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ContentEntity, ContentEntityAdmin)
