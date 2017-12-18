from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList

from .models import Cabinet

logger = logging.getLogger(__name__)


class CabinetListForm(forms.Form):
    def __init__(self, *args, **kwargs):
        help_text = kwargs.pop('help_text', None)
        permission = kwargs.pop('permission', None)
        queryset = kwargs.pop('queryset', Cabinet.objects.all())
        user = kwargs.pop('user', None)

        logger.debug('user: %s', user)
        super(CabinetListForm, self).__init__(*args, **kwargs)

        queryset = AccessControlList.objects.filter_by_access(
            permission=permission, user=user, queryset=queryset
        )

        self.fields['cabinets'] = forms.ModelMultipleChoiceField(
            label=_('Cabinets'), help_text=help_text,
            queryset=queryset, required=False,
            widget=forms.SelectMultiple(attrs={'class': 'select2'})
        )
