from __future__ import unicode_literals

from django.contrib import admin

from .models import StatisticResult


@admin.register(StatisticResult)
class StatisticResultAdmin(admin.ModelAdmin):
    list_display = (
        'slug', 'datetime', 'serialize_data'
    )
