from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    IMAPEmail, POP3Email, StagingFolderSource, WatchFolderSource, WebFormSource
)


@admin.register(IMAPEmail)
class IMAPEmailAdmin(admin.ModelAdmin):
    list_display = (
        'label', 'enabled', 'uncompress', 'host', 'ssl', 'port', 'interval',
        'document_type', 'metadata_attachment_name', 'from_metadata_type',
        'subject_metadata_type', 'store_body'
    )


@admin.register(POP3Email)
class POP3EmailAdmin(admin.ModelAdmin):
    list_display = (
        'label', 'enabled', 'uncompress', 'host', 'ssl', 'port', 'interval',
        'document_type', 'metadata_attachment_name', 'from_metadata_type',
        'subject_metadata_type', 'store_body'
    )


@admin.register(StagingFolderSource)
class StagingFolderSourceAdmin(admin.ModelAdmin):
    list_display = (
        'label', 'enabled', 'folder_path', 'preview_width', 'preview_height',
        'uncompress', 'delete_after_upload'
    )


@admin.register(WatchFolderSource)
class WatchFolderSourceAdmin(admin.ModelAdmin):
    list_display = ('label', 'enabled', 'folder_path', 'uncompress')


@admin.register(WebFormSource)
class WebFormSourceAdmin(admin.ModelAdmin):
    list_display = ('label', 'enabled', 'uncompress')
