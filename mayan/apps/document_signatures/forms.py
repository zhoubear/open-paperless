from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList

from common.forms import DetailForm
from django_gpg.models import Key
from django_gpg.permissions import permission_key_sign

from .models import SignatureBaseModel

logger = logging.getLogger(__name__)


class DocumentVersionSignatureCreateForm(forms.Form):
    key = forms.ModelChoiceField(
        label=_('Key'), queryset=Key.objects.none()
    )

    passphrase = forms.CharField(
        label=_('Passphrase'), required=False,
        widget=forms.widgets.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        logger.debug('user: %s', user)
        super(
            DocumentVersionSignatureCreateForm, self
        ).__init__(*args, **kwargs)

        queryset = AccessControlList.objects.filter_by_access(
            permission_key_sign, user, queryset=Key.objects.private_keys()
        )

        self.fields['key'].queryset = queryset


class DocumentVersionSignatureDetailForm(DetailForm):
    def __init__(self, *args, **kwargs):
        extra_fields = (
            {'label': _('Signature is embedded?'), 'field': 'is_embedded'},
            {
                'label': _('Signature date'), 'field': 'date',
                'widget': forms.widgets.DateInput
            },
            {'label': _('Signature key ID'), 'field': 'key_id'},
            {
                'label': _('Signature key present?'),
                'field': lambda x: x.public_key_fingerprint is not None
            },
        )

        if kwargs['instance'].public_key_fingerprint:
            key = Key.objects.get(
                fingerprint=kwargs['instance'].public_key_fingerprint
            )

            extra_fields += (
                {'label': _('Signature ID'), 'field': 'signature_id'},
                {
                    'label': _('Key fingerprint'),
                    'field': lambda x: key.fingerprint
                },
                {
                    'label': _('Key creation date'),
                    'field': lambda x: key.creation_date,
                    'widget': forms.widgets.DateInput
                },
                {
                    'label': _('Key expiration date'),
                    'field': lambda x: key.expiration_date or _('None'),
                    'widget': forms.widgets.DateInput
                },
                {
                    'label': _('Key length'),
                    'field': lambda x: key.length
                },
                {
                    'label': _('Key algorithm'),
                    'field': lambda x: key.algorithm
                },
                {
                    'label': _('Key user ID'),
                    'field': lambda x: key.user_id
                },
                {
                    'label': _('Key type'),
                    'field': lambda x: key.get_key_type_display()
                },
            )

        kwargs['extra_fields'] = extra_fields
        super(
            DocumentVersionSignatureDetailForm, self
        ).__init__(*args, **kwargs)

    class Meta:
        fields = ()
        model = SignatureBaseModel
