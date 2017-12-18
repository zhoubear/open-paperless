from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from documents.models import Document

from .events import (
    event_document_comment_create, event_document_comment_delete
)

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Comment(models.Model):
    document = models.ForeignKey(
        Document, db_index=True, on_delete=models.CASCADE,
        related_name='comments', verbose_name=_('Document')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE,
        related_name='comments', verbose_name=_('User'),
    )
    # Translators: Comment here is a noun and refers to the actual text stored
    comment = models.TextField(verbose_name=_('Comment'))
    submit_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name=_('Date time submitted')
    )

    def __str__(self):
        return self.comment

    def save(self, *args, **kwargs):
        user = kwargs.pop('_user', None) or self.user
        is_new = not self.pk
        super(Comment, self).save(*args, **kwargs)
        if is_new:
            if user:
                event_document_comment_create.commit(
                    actor=user, target=self.document
                )
                logger.info(
                    'Comment "%s" added to document "%s" by user "%s"',
                    self.comment, self.document, user
                )
            else:
                event_document_comment_create.commit(target=self.document)
                logger.info(
                    'Comment "%s" added to document "%s"', self.comment,
                    self.document
                )

    def delete(self, *args, **kwargs):
        user = kwargs.pop('_user', None)
        super(Comment, self).delete(*args, **kwargs)
        if user:
            event_document_comment_delete.commit(
                actor=user, target=self.document
            )
        else:
            event_document_comment_delete.commit(target=self.document)

    class Meta:
        get_latest_by = 'submit_date'
        ordering = ('-submit_date',)
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
