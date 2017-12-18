from __future__ import unicode_literals

from django import forms
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from common.forms import DetailForm

from .models import Key


class KeyDetailForm(DetailForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']

        extra_fields = (
            {'label': _('Key ID'), 'field': 'key_id'},
            {
                'label': _('User ID'),
                'field': lambda x: escape(instance.user_id),
            },
            {
                'label': _('Creation date'), 'field': 'creation_date',
                'widget': forms.widgets.DateInput
            },
            {
                'label': _('Expiration date'),
                'field': lambda x: instance.expiration_date or _('None'),
                'widget': forms.widgets.DateInput
            },
            {'label': _('Fingerprint'), 'field': 'fingerprint'},
            {'label': _('Length'), 'field': 'length'},
            {'label': _('Algorithm'), 'field': 'algorithm'},
            {'label': _('Type'), 'field': lambda x: instance.get_key_type_display()},
        )

        kwargs['extra_fields'] = extra_fields
        super(KeyDetailForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ()
        model = Key


class KeySearchForm(forms.Form):
    term = forms.CharField(
        label=_('Term'),
        help_text=_('Name, e-mail, key ID or key fingerprint to look for.')
    )
