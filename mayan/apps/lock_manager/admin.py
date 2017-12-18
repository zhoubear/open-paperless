from __future__ import unicode_literals

from django.contrib import admin

from .models import Lock


@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_datetime'
    list_display = ('name', 'creation_datetime', 'timeout')
