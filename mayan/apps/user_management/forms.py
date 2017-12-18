from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active',)


class PasswordForm(forms.Form):
    new_password_1 = forms.CharField(
        label=_('New password'), widget=forms.PasswordInput()
    )
    new_password_2 = forms.CharField(
        label=_('Confirm password'), widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        return super(PasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        password_1 = self.cleaned_data['new_password_1']
        password_2 = self.cleaned_data['new_password_2']
        if password_1 != password_2:
            raise ValidationError('Passwords do not match.')
        else:
            if self.user:
                validate_password(password_2, self.user)

        return self.cleaned_data
