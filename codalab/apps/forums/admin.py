from django.contrib import admin

from . import models


admin.site.register(models.Forum)
admin.site.register(models.Thread)
admin.site.register(models.Post)
