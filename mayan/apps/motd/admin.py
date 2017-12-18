from __future__ import unicode_literals

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('label', 'enabled', 'start_datetime', 'end_datetime')
