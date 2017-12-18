from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from documents.models import DocumentPage, DocumentVersion

from .managers import DocumentPageContentManager


@python_2_unicode_compatible
class DocumentPageContent(models.Model):
    document_page = models.OneToOneField(
        DocumentPage, on_delete=models.CASCADE, related_name='content',
        verbose_name=_('Document page')
    )
    content = models.TextField(blank=True, verbose_name=_('Content'))

    objects = DocumentPageContentManager()

    def __str__(self):
        return force_text(self.document_page)

    class Meta:
        verbose_name = _('Document page content')
        verbose_name_plural = _('Document pages contents')


@python_2_unicode_compatible
class DocumentVersionParseError(models.Model):
    document_version = models.ForeignKey(
        DocumentVersion, on_delete=models.CASCADE,
        related_name='parsing_errors', verbose_name=_('Document version')
    )
    datetime_submitted = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date time submitted')
    )
    result = models.TextField(blank=True, null=True, verbose_name=_('Result'))

    def __str__(self):
        return force_text(self.document_version)

    class Meta:
        ordering = ('datetime_submitted',)
        verbose_name = _('Document version parse error')
        verbose_name_plural = _('Document version parse errors')
