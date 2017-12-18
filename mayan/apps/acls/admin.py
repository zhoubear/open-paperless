from __future__ import unicode_literals

from django.contrib import admin

from .models import AccessControlList


@admin.register(AccessControlList)
class AccessControlListAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    list_display = ('pk', 'role', 'content_type', 'content_object')
    list_display_links = ('pk',)
    list_filter = ('content_type',)
    related_lookup_fields = {
        'generic': (('content_type', 'object_id'),),
    }
