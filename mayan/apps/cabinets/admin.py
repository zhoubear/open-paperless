from __future__ import unicode_literals

from django.contrib import admin

from .models import Cabinet

from mptt.admin import MPTTModelAdmin


@admin.register(Cabinet)
class CabinetAdmin(MPTTModelAdmin):
    filter_horizontal = ('documents',)
    list_display = ('label',)
