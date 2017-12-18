from __future__ import unicode_literals

import json
import logging

from django.core import mail
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from .utils import split_recipient_list

logger = logging.getLogger(__name__)


class LogEntry(models.Model):
    datetime = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_('Date time')
    )
    message = models.TextField(
        blank=True, editable=False, verbose_name=_('Message')
    )

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('-datetime',)
        verbose_name = _('Log entry')
        verbose_name_plural = _('Log entries')


class UserMailer(models.Model):
    label = models.CharField(
        max_length=128, unique=True, verbose_name=_('Label')
    )
    default = models.BooleanField(
        default=True, help_text=_(
            'If default, this mailing profile will be pre-selected on the '
            'document mailing form.'
        ), verbose_name=_('Default')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    backend_path = models.CharField(
        max_length=128,
        help_text=_('The dotted Python path to the backend class.'),
        verbose_name=_('Backend path')
    )
    backend_data = models.TextField(
        blank=True, verbose_name=_('Backend data')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _('User mailer')
        verbose_name_plural = _('User mailers')

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.default:
            UserMailer.objects.select_for_update().exclude(pk=self.pk).update(
                default=False
            )

        return super(UserMailer, self).save(*args, **kwargs)

    def backend_label(self):
        return self.get_backend().label

    def get_backend(self):
        return import_string(self.backend_path)

    def get_connection(self):
        return mail.get_connection(
            backend=self.get_backend().class_path, **self.loads()
        )

    def loads(self):
        return json.loads(self.backend_data)

    def dumps(self, data):
        self.backend_data = json.dumps(data)
        self.save()

    def send(self, subject='', body='', to=None, document=None, as_attachment=False):
        recipient_list = split_recipient_list(recipients=[to])

        with self.get_connection() as connection:
            email_message = mail.EmailMultiAlternatives(
                subject=subject, body=body, to=recipient_list,
                connection=connection
            )

            if as_attachment:
                with document.open() as descriptor:
                    email_message.attach(
                        filename=document.label, content=descriptor.read(),
                        mimetype=document.file_mimetype
                    )

            try:
                email_message.send()
            except Exception as exception:
                self.error_log.create(message=exception)
            else:
                self.error_log.all().delete()

    def test(self, to):
        self.send(to=to, subject=_('Test email from Mayan EDMS'))


class UserMailerLogEntry(models.Model):
    user_mailer = models.ForeignKey(
        UserMailer, on_delete=models.CASCADE, related_name='error_log',
        verbose_name=_('User mailer')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_('Date time')
    )
    message = models.TextField(
        blank=True, editable=False, verbose_name=_('Message')
    )

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('-datetime',)
        verbose_name = _('User mailer log entry')
        verbose_name_plural = _('User mailer log entries')
