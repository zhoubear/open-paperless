from __future__ import unicode_literals

import os

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from .classes import Filter, Package
from .models import UserLocaleProfile
from .utils import return_attrib
from .widgets import (
    DetailSelectMultiple, DisableableSelectWidget, PlainWidget
)


class ChoiceForm(forms.Form):
    """
    Form to be used in side by side templates used to add or remove
    items from a many to many field
    """
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        label = kwargs.pop('label', _('Selection'))
        help_text = kwargs.pop('help_text', None)
        disabled_choices = kwargs.pop('disabled_choices', ())
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields['selection'].choices = choices
        self.fields['selection'].label = label
        self.fields['selection'].help_text = help_text
        self.fields['selection'].widget.disabled_choices = disabled_choices
        self.fields['selection'].widget.attrs.update(
            {'size': 14, 'class': 'choice_form'}
        )

    selection = forms.MultipleChoiceField(widget=DisableableSelectWidget())


class DetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.extra_fields = kwargs.pop('extra_fields', ())
        super(DetailForm, self).__init__(*args, **kwargs)

        for extra_field in self.extra_fields:
            result = return_attrib(self.instance, extra_field['field'])
            label = 'label' in extra_field and extra_field['label'] or None
            # TODO: Add others result types <=> Field types
            if isinstance(result, models.query.QuerySet):
                self.fields[extra_field['field']] = \
                    forms.ModelMultipleChoiceField(
                        queryset=result, label=label)
            else:
                self.fields[extra_field['field']] = forms.CharField(
                    label=extra_field['label'],
                    initial=return_attrib(
                        self.instance,
                        extra_field['field'], None
                    ),
                    widget=extra_field.get('widget', PlainWidget)
                )

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.SelectMultiple):
                self.fields[field_name].widget = DetailSelectMultiple(
                    choices=field.widget.choices,
                    attrs=field.widget.attrs,
                    queryset=getattr(field, 'queryset', None),
                )
                self.fields[field_name].help_text = ''
            elif isinstance(field.widget, forms.widgets.Select):
                self.fields[field_name].widget = DetailSelectMultiple(
                    choices=field.widget.choices,
                    attrs=field.widget.attrs,
                    queryset=getattr(field, 'queryset', None),
                )
                self.fields[field_name].help_text = ''

        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs.update(
                {'readonly': 'readonly'}
            )


class DynamicFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema')
        super(DynamicFormMixin, self).__init__(*args, **kwargs)

        widgets = self.schema.get('widgets', {})
        field_order = self.schema.get(
            'field_order', self.schema['fields'].keys()
        )

        for field_name in field_order:
            field_data = self.schema['fields'][field_name]
            field_class = import_string(field_data['class'])
            kwargs = {
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'initial': field_data.get('default', None),
                'help_text': field_data.get('help_text'),
            }
            if widgets and field_name in widgets:
                widget = widgets[field_name]
                kwargs['widget'] = import_string(
                    widget['class']
                )(**widget.get('kwargs', {}))

            kwargs.update(field_data.get('kwargs', {}))
            self.fields[field_name] = field_class(**kwargs)


class DynamicForm(DynamicFormMixin, forms.Form):
    pass


class DynamicModelForm(DynamicFormMixin, forms.ModelForm):
    pass


class FileDisplayForm(forms.Form):
    text = forms.CharField(
        label='',
        widget=forms.widgets.Textarea(
            attrs={'cols': 40, 'rows': 20, 'readonly': 'readonly'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(FileDisplayForm, self).__init__(*args, **kwargs)
        changelog_path = os.path.join(
            settings.BASE_DIR, os.sep.join(self.DIRECTORY), self.FILENAME
        )
        fd = open(changelog_path)
        self.fields['text'].initial = fd.read()
        fd.close()


class FilterForm(forms.Form):
    filter_slug = forms.ChoiceField(label=_('Filter'))

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['filter_slug'].choices = Filter.all().items()


class LicenseForm(FileDisplayForm):
    DIRECTORY = ()
    FILENAME = 'LICENSE'


class LocaleProfileForm(forms.ModelForm):
    class Meta:
        fields = ('language', 'timezone')
        model = UserLocaleProfile
        widgets = {
            'language': forms.Select(
                attrs={
                    'class': 'select2'
                }
            ),
            'timezone': forms.Select(
                attrs={
                    'class': 'select2'
                }
            )
        }


class LocaleProfileForm_view(DetailForm):
    class Meta:
        fields = ('language', 'timezone')
        model = UserLocaleProfile


class PackagesLicensesForm(forms.Form):
    text = forms.CharField(
        label='',
        widget=forms.widgets.Textarea(
            attrs={'cols': 40, 'rows': 20, 'readonly': 'readonly'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(PackagesLicensesForm, self).__init__(*args, **kwargs)
        self.fields['text'].initial = '\n\n'.join(
            ['{}\n{}'.format(package.label, package.license_text) for package in Package.get_all()]
        )


class UserForm(forms.ModelForm):
    """
    Form used to edit an user's mininal fields by the user himself
    """

    class Meta:
        fields = ('username', 'first_name', 'last_name', 'email')
        model = get_user_model()


class UserForm_view(DetailForm):
    """
    Form used to display an user's public details
    """

    class Meta:
        fields = (
            'username', 'first_name', 'last_name', 'email', 'last_login',
            'date_joined', 'groups'
        )
        model = get_user_model()
