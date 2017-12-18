from __future__ import absolute_import, unicode_literals

from datetime import date
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .exceptions import NeedPassphrase, PassphraseError
from .literals import (
    ERROR_MSG_NEED_PASSPHRASE, ERROR_MSG_BAD_PASSPHRASE,
    ERROR_MSG_GOOD_PASSPHRASE, KEY_TYPE_CHOICES, KEY_TYPE_SECRET,
    OUTPUT_MESSAGE_CONTAINS_PRIVATE_KEY
)
from .managers import KeyManager
from .runtime import gpg_backend

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Key(models.Model):
    """
    Fields:
    * key_type - Will show private or public, the only two types of keys in
    a public key infrastructure, the kind used in Mayan.
    """
    key_data = models.TextField(
        help_text=_('ASCII armored version of the key.'),
        verbose_name=_('Key data')
    )
    creation_date = models.DateField(
        editable=False, verbose_name=_('Creation date')
    )
    expiration_date = models.DateField(
        blank=True, editable=False, null=True,
        verbose_name=_('Expiration date')
    )
    fingerprint = models.CharField(
        editable=False, max_length=40, unique=True,
        verbose_name=_('Fingerprint')
    )
    length = models.PositiveIntegerField(
        editable=False, verbose_name=_('Length')
    )
    algorithm = models.PositiveIntegerField(
        editable=False, verbose_name=_('Algorithm')
    )
    user_id = models.TextField(editable=False, verbose_name=_('User ID'))
    key_type = models.CharField(
        choices=KEY_TYPE_CHOICES, editable=False, max_length=3,
        verbose_name=_('Type')
    )

    objects = KeyManager()

    class Meta:
        verbose_name = _('Key')
        verbose_name_plural = _('Keys')

    def clean(self):
        import_results = gpg_backend.import_key(key_data=self.key_data)

        if not import_results.count:
            raise ValidationError(_('Invalid key data'))

        if Key.objects.filter(fingerprint=import_results.fingerprints[0]).exists():
            raise ValidationError(_('Key already exists.'))

    def get_absolute_url(self):
        return reverse('django_gpg:key_detail', args=(self.pk,))

    def save(self, *args, **kwargs):
        import_results, key_info = gpg_backend.import_and_list_keys(
            key_data=self.key_data
        )
        logger.debug('key_info: %s', key_info)

        self.algorithm = key_info['algo']
        self.creation_date = date.fromtimestamp(int(key_info['date']))
        if key_info['expires']:
            self.expiration_date = date.fromtimestamp(int(key_info['expires']))
        self.fingerprint = key_info['fingerprint']
        self.length = int(key_info['length'])
        self.user_id = key_info['uids'][0]
        if OUTPUT_MESSAGE_CONTAINS_PRIVATE_KEY in import_results.results[0]['text']:
            self.key_type = KEY_TYPE_SECRET
        else:
            self.key_type = key_info['type']

        super(Key, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.key_id, self.user_id)

    def sign_file(self, file_object, passphrase=None, clearsign=False, detached=False, binary=False, output=None):
        # WARNING: using clearsign=True and subsequent decryption corrupts the
        # file. Appears to be a problem in python-gnupg or gpg itself.
        # https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=55647
        # "The problems differ from run to run and file to
        # file, and appear to be due to random data being inserted in the
        # output data stream."

        file_sign_results = gpg_backend.sign_file(
            file_object=file_object, key_data=self.key_data,
            passphrase=passphrase, clearsign=clearsign, detached=detached,
            binary=binary, output=output
        )

        logger.debug('file_sign_results.stderr: %s', file_sign_results.stderr)

        if ERROR_MSG_NEED_PASSPHRASE in file_sign_results.stderr:
            if ERROR_MSG_BAD_PASSPHRASE in file_sign_results.stderr:
                raise PassphraseError
            elif ERROR_MSG_GOOD_PASSPHRASE not in file_sign_results.stderr:
                raise NeedPassphrase

        return file_sign_results

    @property
    def key_id(self):
        return self.fingerprint[-8:]
