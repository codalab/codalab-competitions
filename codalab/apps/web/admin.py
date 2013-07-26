from django.contrib import admin
import models
from django.contrib.contenttypes import generic
from mptt.admin import MPTTModelAdmin

class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Dataset, DatasetAdmin)

class PhaseInlineAdmin(admin.TabularInline):
    model = models.CompetitionPhase

class PageContainerGenericInline(generic.GenericTabularInline):
    model = models.PageContainer

class ParticipantInlineAdmin(admin.TabularInline):
    model = models.CompetitionParticipant

class CompetitionAdmin(admin.ModelAdmin):
    inlines = [ PageContainerGenericInline,
               PhaseInlineAdmin,
               ParticipantInlineAdmin
               ]               
admin.site.register(models.Competition, CompetitionAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.CompetitionParticipant, ParticipantAdmin)

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

class ContentEntityAdmin(MPTTModelAdmin):
    pass
admin.site.register(models.ContentEntity, ContentEntityAdmin)

class ExternalFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ExternalFile, ExternalFileAdmin)

class ExternalFileTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ExternalFileType, ExternalFileTypeAdmin)

class ExternalFileSourceAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ExternalFileSource, ExternalFileSourceAdmin)

class PageGenAdmin(admin.TabularInline):
    model = models.Page

class PageContainerAdmin(admin.ModelAdmin):
    inlines = [PageGenAdmin]
admin.site.register(models.PageContainer, PageContainerAdmin)

class PageAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Page, PageAdmin)

class BundleAdmin(admin.ModelAdmin):pass
admin.site.register(models.Bundle, BundleAdmin)
