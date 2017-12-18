from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import MessageManager


@python_2_unicode_compatible
class Message(models.Model):
    label = models.CharField(
        max_length=32, help_text=_('Short description of this message.'),
        verbose_name=_('Label')
    )
    message = models.TextField(
        help_text=_('The actual message to be displayed.'),
        verbose_name=_('Message')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    start_datetime = models.DateTimeField(
        blank=True, help_text=_(
            'Date and time after which this message will be displayed.'
        ), null=True, verbose_name=_('Start date time')
    )
    end_datetime = models.DateTimeField(
        blank=True, help_text=_(
            'Date and time until when this message is to be displayed.'
        ), null=True, verbose_name=_('End date time')
    )

    objects = MessageManager()

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.label
