from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text
from django.utils.html import conditional_escape


def get_document_ocr_content(document):
    DocumentPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentPageOCRContent'
    )

    for page in document.pages.all():
        try:
            page_content = page.ocr_content.content
        except DocumentPageOCRContent.DoesNotExist:
            pass
        else:
            yield conditional_escape(force_text(page_content))
