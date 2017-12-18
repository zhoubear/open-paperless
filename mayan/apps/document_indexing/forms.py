from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from common.classes import ModelAttribute
from documents.models import Document

from .models import Index, IndexTemplateNode


class IndexListForm(forms.Form):
    indexes = forms.ModelMultipleChoiceField(
        help_text=_('Indexes to be queued for rebuilding.'),
        label=_('Indexes'), queryset=Index.objects.filter(enabled=True),
        required=False, widget=forms.widgets.CheckboxSelectMultiple()
    )


class IndexTemplateNodeForm(forms.ModelForm):
    """
    A standard model form to allow users to create a new index template node
    """
    def __init__(self, *args, **kwargs):
        super(IndexTemplateNodeForm, self).__init__(*args, **kwargs)
        self.fields['index'].widget = forms.widgets.HiddenInput()
        self.fields['parent'].widget = forms.widgets.HiddenInput()
        self.fields['expression'].help_text = ' '.join(
            [
                force_text(self.fields['expression'].help_text),
                ModelAttribute.help_text_for(
                    Document, type_names=['indexing']
                ).replace('\n', '<br>')
            ]
        )

    class Meta:
        fields = ('parent', 'index', 'expression', 'enabled', 'link_documents')
        model = IndexTemplateNode
