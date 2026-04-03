from django.contrib import admin
from . import models
from apps.authenz.models import ClUser


def DeactivateAccount(modeladmin, request, queryset):
    for obj in queryset:
        user = ClUser.objects.get(id=obj.started_by_id)
        print(user.username)
        user.is_active = False
        user.save()
    queryset.delete()
DeactivateAccount.short_description = "Deactivate Account and Delete Thread"


def DeactivateAccountPost(modeladmin, request, queryset):
    for obj in queryset:
        user = ClUser.objects.get(id=obj.posted_by_id)
        print(user.username)
        user.is_active = False
        user.save()
    queryset.delete()
DeactivateAccountPost.short_description = "Deactivate Account and Delete Post"


class ThreadAdmin(admin.ModelAdmin):
    search_fields  = ['title', 'started_by__username']
    list_display = ['title', 'started_by']
    actions = [DeactivateAccount]
admin.site.register(models.Thread, ThreadAdmin)

class PostAdmin(admin.ModelAdmin):
    search_fields  = ['content', 'posted_by__username']
    list_display = ['content', 'posted_by']
    actions = [DeactivateAccountPost]
admin.site.register(models.Post, PostAdmin)


admin.site.register(models.Forum)
