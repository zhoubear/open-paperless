from __future__ import unicode_literals

from django.contrib import admin

from .models import Key


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = (
        'key_id', 'user_id', 'creation_date', 'expiration_date', 'key_type'
    )
    list_filter = ('key_type',)
    readonly_fields = list_display + ('fingerprint', 'length', 'algorithm')
    search_fields = ('key_id', 'user_id',)
