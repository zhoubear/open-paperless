from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text
from django.utils.html import conditional_escape


def get_document_content(document):
    DocumentPageContent = apps.get_model(
        app_label='document_parsing', model_name='DocumentPageContent'
    )

    for page in document.pages.all():
        try:
            page_content = page.content.content
        except DocumentPageContent.DoesNotExist:
            pass
        else:
            yield conditional_escape(force_text(page_content))
