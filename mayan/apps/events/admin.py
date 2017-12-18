from __future__ import unicode_literals

from django.contrib import admin

from .models import EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('name', '__str__')
