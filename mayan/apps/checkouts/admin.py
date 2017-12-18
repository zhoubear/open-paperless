from __future__ import unicode_literals

from django.contrib import admin

from .models import DocumentCheckout


@admin.register(DocumentCheckout)
class DocumentCheckoutAdmin(admin.ModelAdmin):
    list_display = (
        'document', 'checkout_datetime', 'expiration_datetime', 'user',
        'block_new_version'
    )
    list_display_links = None
