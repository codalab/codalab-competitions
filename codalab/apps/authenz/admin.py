from django.contrib import admin
import csv
from .models import ClUser
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(
        content_type="text/csv",
    )
    writer = csv.writer(response)
    writer.writerow(["ID", "Active", "Email"])
    for obj in queryset:
        if obj.is_active and obj.email:
            writer.writerow(
                [
                    obj.id,
                    obj.is_active,
                    obj.email,
                ]
            )
    return response


class userExpansion(admin.ModelAdmin):
    actions = [export_as_csv]


admin.site.register(ClUser, userExpansion)
