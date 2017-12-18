from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from documents.models import Document

from .events import event_document_check_out
from .exceptions import DocumentAlreadyCheckedOut
from .managers import DocumentCheckoutManager, NewVersionBlockManager

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class DocumentCheckout(models.Model):
    """
    Model to store the state and information of a document checkout
    """
    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, verbose_name=_('Document')
    )
    checkout_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Check out date and time')
    )
    expiration_datetime = models.DateTimeField(
        help_text=_(
            'Amount of time to hold the document checked out in minutes.'
        ),
        verbose_name=_('Check out expiration date and time')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    block_new_version = models.BooleanField(
        default=True,
        help_text=_(
            'Do not allow new version of this document to be uploaded.'
        ),
        verbose_name=_('Block new version upload')
    )

    objects = DocumentCheckoutManager()

    def __str__(self):
        return force_text(self.document)

    def clean(self):
        if self.expiration_datetime < now():
            raise ValidationError(
                _('Check out expiration date and time must be in the future.')
            )

    def delete(self, *args, **kwargs):
        # TODO: enclose in transaction
        NewVersionBlock.objects.unblock(self.document)
        super(DocumentCheckout, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('checkout:checkout_info', args=(self.document.pk,))

    def save(self, *args, **kwargs):
        # TODO: enclose in transaction
        new_checkout = not self.pk
        if not new_checkout or self.document.is_checked_out():
            raise DocumentAlreadyCheckedOut

        result = super(DocumentCheckout, self).save(*args, **kwargs)
        if new_checkout:
            event_document_check_out.commit(
                actor=self.user, target=self.document
            )
            if self.block_new_version:
                NewVersionBlock.objects.block(self.document)

            logger.info(
                'Document "%s" checked out by user "%s"',
                self.document, self.user
            )

        return result

    class Meta:
        verbose_name = _('Document checkout')
        verbose_name_plural = _('Document checkouts')


class NewVersionBlock(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_('Document')
    )

    objects = NewVersionBlockManager()

    class Meta:
        verbose_name = _('New version block')
        verbose_name_plural = _('New version blocks')
