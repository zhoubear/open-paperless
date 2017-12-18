from __future__ import unicode_literals

from django.contrib import admin

from .models import LogEntry, UserMailer


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ('datetime', 'message')
    readonly_fields = ('datetime', 'message')


@admin.register(UserMailer)
class UserMailerAdmin(admin.ModelAdmin):
    list_display = (
        'label', 'default', 'enabled', 'backend_path', 'backend_data'
    )
