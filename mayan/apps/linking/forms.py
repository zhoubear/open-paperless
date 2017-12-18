from __future__ import unicode_literals

from django import forms
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from common.classes import ModelAttribute
from documents.models import Document

from .models import SmartLink, SmartLinkCondition


class SmartLinkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SmartLinkForm, self).__init__(*args, **kwargs)
        self.fields['dynamic_label'].help_text = ' '.join(
            [
                force_text(self.fields['dynamic_label'].help_text),
                ModelAttribute.help_text_for(
                    Document, type_names=['field', 'related', 'property']
                ).replace('\n', '<br>')
            ]
        )

    class Meta:
        fields = ('label', 'dynamic_label', 'enabled')
        model = SmartLink


class SmartLinkConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SmartLinkConditionForm, self).__init__(*args, **kwargs)
        self.fields['foreign_document_data'] = forms.ChoiceField(
            choices=ModelAttribute.get_choices_for(
                Document, type_names=['field', 'query']
            ), label=_('Foreign document attribute')
        )
        self.fields['expression'].help_text = ' '.join(
            [
                force_text(self.fields['expression'].help_text),
                ModelAttribute.help_text_for(
                    Document, type_names=['field', 'related', 'property']
                ).replace('\n', '<br>')
            ]
        )

    class Meta:
        model = SmartLinkCondition
        exclude = ('smart_link',)
