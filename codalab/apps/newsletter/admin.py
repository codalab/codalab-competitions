from django.contrib import admin

from .models import NewsletterSubscription


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added',)


admin.site.register(NewsletterSubscription, NewsletterAdmin)
