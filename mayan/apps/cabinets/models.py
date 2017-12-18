from __future__ import absolute_import, unicode_literals

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import connection, models, transaction
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view

from .events import event_cabinets_add_document, event_cabinets_remove_document
from .search import cabinet_search  # NOQA


@python_2_unicode_compatible
class Cabinet(MPTTModel):
    parent = TreeForeignKey(
        'self', blank=True, db_index=True, null=True,
        on_delete=models.CASCADE, related_name='children'
    )
    label = models.CharField(max_length=128, verbose_name=_('Label'))
    documents = models.ManyToManyField(
        Document, blank=True, related_name='cabinets',
        verbose_name=_('Documents')
    )

    class Meta:
        ordering = ('parent__label', 'label')
        # unique_together doesn't work if there is a FK
        # https://code.djangoproject.com/ticket/1751
        unique_together = ('parent', 'label')
        verbose_name = _('Cabinet')
        verbose_name_plural = _('Cabinets')

    def __str__(self):
        return self.get_full_path()

    def add_document(self, document, user=None):
        self.documents.add(document)
        event_cabinets_add_document.commit(
            action_object=self, actor=user, target=document
        )

    def get_absolute_url(self):
        return reverse('cabinets:cabinet_view', args=(self.pk,))

    def get_document_count(self, user):
        return self.get_documents_queryset(user=user).count()

    def get_documents_queryset(self, user):
        return AccessControlList.objects.filter_by_access(
            permission_document_view, user, queryset=self.documents
        )

    def get_full_path(self):
        result = []
        for node in self.get_ancestors(include_self=True):
            result.append(node.label)

        return ' / '.join(result)

    def remove_document(self, document, user=None):
        self.documents.remove(document)
        event_cabinets_remove_document.commit(
            action_object=self, actor=user, target=document
        )

    def validate_unique(self, exclude=None):
        # Explicit validation of uniqueness of parent+label as the provided
        # unique_together check in Meta is not working for all 100% cases
        # when there is a FK in the unique_together tuple
        # https://code.djangoproject.com/ticket/1751

        with transaction.atomic():
            if connection.vendor == 'oracle':
                queryset = Cabinet.objects.filter(parent=self.parent, label=self.label)
            else:
                queryset = Cabinet.objects.select_for_update().filter(parent=self.parent, label=self.label)

            if queryset.exists():
                params = {
                    'model_name': _('Cabinet'),
                    'field_labels': _('Parent and Label')
                }
                raise ValidationError(
                    {
                        NON_FIELD_ERRORS: [
                            ValidationError(
                                message=_(
                                    '%(model_name)s with this %(field_labels)s already '
                                    'exists.'
                                ), code='unique_together', params=params,
                            )
                        ],
                    },
                )


class DocumentCabinet(Cabinet):
    class Meta:
        proxy = True
        verbose_name = _('Document cabinet')
        verbose_name_plural = _('Document cabinets')
