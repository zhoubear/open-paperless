from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList

from .models import Tag
from .permissions import permission_tag_view
from .widgets import TagFormWidget

logger = logging.getLogger(__name__)


class TagMultipleSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        help_text = kwargs.pop('help_text', None)
        permission = kwargs.pop('permission', permission_tag_view)
        queryset = kwargs.pop('queryset', Tag.objects.all())
        user = kwargs.pop('user', None)

        logger.debug('user: %s', user)
        super(TagMultipleSelectionForm, self).__init__(*args, **kwargs)

        queryset = AccessControlList.objects.filter_by_access(
            permission=permission, queryset=queryset, user=user
        )

        self.fields['tags'] = forms.ModelMultipleChoiceField(
            label=_('Tags'), help_text=help_text,
            queryset=queryset, required=False,
            widget=TagFormWidget(
                attrs={'class': 'select2-tags'}, queryset=queryset
            )
        )
