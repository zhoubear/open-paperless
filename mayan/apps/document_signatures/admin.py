from __future__ import unicode_literals

from django.contrib import admin

from .models import DetachedSignature, EmbeddedSignature


@admin.register(DetachedSignature)
class DetachedSignatureAdmin(admin.ModelAdmin):
    list_display = (
        'document_version', 'date', 'key_id', 'signature_id',
        'public_key_fingerprint', 'signature_file'
    )
    list_display_links = ('document_version',)


@admin.register(EmbeddedSignature)
class EmbeddedSignatureAdmin(admin.ModelAdmin):
    list_display = (
        'document_version', 'date', 'key_id', 'signature_id',
        'public_key_fingerprint'
    )
    list_display_links = ('document_version',)
