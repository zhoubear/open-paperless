from __future__ import unicode_literals

from django.utils.html import format_html_join


def get_metadata_string(document):
    """
    Return a formated representation of a document's metadata values
    """
    return format_html_join(
        '\n', '<div class="metadata-display"><b>{}: </b><span data-metadata-type="{}" data-pk="{}">{}</span></div>',
        (
            (
                document_metadata.metadata_type, document_metadata.metadata_type_id, document_metadata.id, document_metadata.value
            ) for document_metadata in document.metadata.all()
        )
    )
