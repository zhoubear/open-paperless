from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.utils.translation import string_concat, ugettext_lazy as _

from .classes import MetadataLookup
from .models import MetadataType


class DocumentMetadataForm(forms.Form):
    id = forms.CharField(label=_('ID'), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Name'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    value = forms.CharField(
        label=_('Value'), required=False, widget=forms.TextInput(
            attrs={'class': 'metadata-value'}
        )
    )
    update = forms.BooleanField(
        initial=True, label=_('Update'), required=False
    )

    class Media:
        js = ('metadata/js/metadata_form.js',)

    def __init__(self, *args, **kwargs):
        super(DocumentMetadataForm, self).__init__(*args, **kwargs)

        # Set form fields initial values
        if 'initial' in kwargs:
            self.metadata_type = kwargs['initial']['metadata_type']
            self.document_type = kwargs['initial']['document_type']
            required_string = ''

            required = self.metadata_type.get_required_for(
                document_type=self.document_type
            )

            if required:
                self.fields['value'].required = True
                required_string = ' (%s)' % _('Required')
            else:
                self.fields['value'].required = False
                self.fields['update'].initial = False

            self.fields['name'].initial = '%s%s' % (
                (
                    self.metadata_type.label if self.metadata_type.label else self.metadata_type.name
                ),
                required_string
            )
            self.fields['id'].initial = self.metadata_type.pk

            if self.metadata_type.lookup:
                try:
                    self.fields['value'] = forms.ChoiceField(
                        label=self.fields['value'].label
                    )
                    choices = self.metadata_type.get_lookup_values()
                    choices = zip(choices, choices)
                    if not required:
                        choices.insert(0, ('', '------'))
                    self.fields['value'].choices = choices
                    self.fields['value'].required = required
                    self.fields['value'].widget.attrs.update(
                        {'class': 'metadata-value'}
                    )
                except Exception as exception:
                    self.fields['value'].initial = _(
                        'Lookup value error: %s'
                    ) % exception
                    self.fields['value'].widget = forms.TextInput(
                        attrs={'readonly': 'readonly'}
                    )

            if self.metadata_type.default:
                try:
                    self.fields[
                        'value'
                    ].initial = self.metadata_type.get_default_value()
                except Exception as exception:
                    self.fields['value'].initial = _(
                        'Default value error: %s'
                    ) % exception
                    self.fields['value'].widget = forms.TextInput(
                        attrs={'readonly': 'readonly'}
                    )

    def clean(self):
        metadata_type = getattr(self, 'metadata_type', None)

        if metadata_type:
            required = self.metadata_type.get_required_for(
                document_type=self.document_type
            )
            if required and not self.cleaned_data.get('update'):
                raise ValidationError(
                    _(
                        '"%s" is required for this document type.'
                    ) % self.metadata_type.label
                )

        if self.cleaned_data.get('update') and hasattr(self, 'metadata_type'):
            self.cleaned_data['value'] = self.metadata_type.validate_value(
                document_type=self.document_type,
                value=self.cleaned_data.get('value')
            )

        return self.cleaned_data


DocumentMetadataFormSet = formset_factory(DocumentMetadataForm, extra=0)


class DocumentAddMetadataForm(forms.Form):
    metadata_type = forms.ModelMultipleChoiceField(
        help_text=_('Metadata types to be added to the selected documents.'),
        label=_('Metadata type'), queryset=MetadataType.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'select2'},
        )
    )

    def __init__(self, *args, **kwargs):
        document_type = kwargs.pop('document_type', None)

        if document_type:
            queryset = kwargs.pop(
                'queryset', MetadataType.objects.get_for_document_type(
                    document_type=document_type
                )
            )
        else:
            queryset = MetadataType.objects.none()

        super(DocumentAddMetadataForm, self).__init__(*args, **kwargs)

        self.fields['metadata_type'].queryset = queryset


class MetadataTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MetadataTypeForm, self).__init__(*args, **kwargs)
        self.fields['lookup'].help_text = string_concat(
            self.fields['lookup'].help_text,
            _(' Available template context variables: '),
            MetadataLookup.get_as_help_text()
        )

    class Meta:
        fields = ('name', 'label', 'default', 'lookup', 'validation', 'parser')
        model = MetadataType


class DocumentMetadataRemoveForm(DocumentMetadataForm):
    update = forms.BooleanField(
        initial=False, label=_('Remove'), required=False
    )

    def __init__(self, *args, **kwargs):
        super(DocumentMetadataRemoveForm, self).__init__(*args, **kwargs)
        self.fields.pop('value')


DocumentMetadataRemoveFormSet = formset_factory(
    DocumentMetadataRemoveForm, extra=0
)


class DocumentTypeMetadataTypeRelationshipForm(forms.Form):
    label = forms.CharField(
        label=_('Label'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    relationship = forms.ChoiceField(
        label=_('Relationship'),
        widget=forms.RadioSelect(), choices=(
            ('none', _('None')),
            ('optional', _('Optional')),
            ('required', _('Required')),
        )
    )

    def __init__(self, *args, **kwargs):
        super(DocumentTypeMetadataTypeRelationshipForm, self).__init__(
            *args, **kwargs
        )
        if self.initial['main_model'] == 'metadata_type':
            self.fields['label'].initial = self.initial['document_type'].label
        else:
            self.fields['label'].initial = self.initial['metadata_type'].label

        relationship = self.initial['document_type'].metadata.filter(
            metadata_type=self.initial['metadata_type']
        )
        if relationship.exists():
            if relationship.get().required:
                self.fields['relationship'].initial = 'required'
            else:
                self.fields['relationship'].initial = 'optional'
        else:
            self.fields['relationship'].initial = 'none'

    def save(self):
        relationship = self.initial['document_type'].metadata.filter(
            metadata_type=self.initial['metadata_type']
        )
        if self.cleaned_data['relationship'] == 'none':
            relationship.delete()
        elif self.cleaned_data['relationship'] == 'optional':
            if relationship.exists():
                instance = relationship.get()
                instance.required = False
                instance.save()
            else:
                relationship.create(
                    document_type=self.initial['document_type'],
                    metadata_type=self.initial['metadata_type']
                )
        elif self.cleaned_data['relationship'] == 'required':
            if relationship.exists():
                instance = relationship.get()
                instance.required = True
                instance.save()
            else:
                relationship.create(
                    document_type=self.initial['document_type'],
                    metadata_type=self.initial['metadata_type'], required=True
                )


DocumentTypeMetadataTypeRelationshipFormSet = formset_factory(
    DocumentTypeMetadataTypeRelationshipForm, extra=0
)
