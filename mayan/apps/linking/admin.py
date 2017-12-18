from __future__ import unicode_literals

from django.contrib import admin

from .models import SmartLink, SmartLinkCondition


class SmartLinkConditionInline(admin.StackedInline):
    model = SmartLinkCondition
    extra = 1
    classes = ('collapse-open',)
    allow_add = True


@admin.register(SmartLink)
class SmartLinkAdmin(admin.ModelAdmin):
    def document_type_list(self, instance):
        return ','.join(
            instance.document_types.values_list('label', flat=True)
        )

    filter_horizontal = ('document_types',)
    inlines = (SmartLinkConditionInline,)
    list_display = ('label', 'dynamic_label', 'enabled', 'document_type_list')
