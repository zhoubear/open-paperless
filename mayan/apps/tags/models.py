from __future__ import absolute_import, unicode_literals

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from colorful.fields import RGBColorField

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view

from .events import event_tag_attach, event_tag_remove


@python_2_unicode_compatible
class Tag(models.Model):
    label = models.CharField(
        db_index=True, max_length=128, unique=True, verbose_name=_('Label')
    )
    color = RGBColorField(verbose_name=_('Color'))
    documents = models.ManyToManyField(
        Document, related_name='tags', verbose_name=_('Documents')
    )

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('tags:tag_tagged_item_list', args=(str(self.pk),))

    class Meta:
        ordering = ('label',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def attach_to(self, document, user=None):
        self.documents.add(document)
        event_tag_attach.commit(
            action_object=self, actor=user, target=document
        )

    def get_document_count(self, user):
        queryset = AccessControlList.objects.filter_by_access(
            permission_document_view, user, queryset=self.documents
        )

        return queryset.count()

    def remove_from(self, document, user=None):
        self.documents.remove(document)
        event_tag_remove.commit(
            action_object=self, actor=user, target=document
        )


class DocumentTag(Tag):
    class Meta:
        proxy = True
        verbose_name = _('Document tag')
        verbose_name_plural = _('Document tags')
