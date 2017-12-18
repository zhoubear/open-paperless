from __future__ import unicode_literals

import warnings

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from common.widgets import EmailInput


class EmailAuthenticationForm(forms.Form):
    """
    A form to use email address authentication
    """
    email = forms.CharField(
        label=_('Email'), max_length=254, widget=EmailInput()
    )
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput
    )
    remember_me = forms.BooleanField(label=_('Remember me'), required=False)

    error_messages = {
        'invalid_login': _('Please enter a correct email and password. '
                           'Note that the password field is case-sensitive.'),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data

    def check_for_test_cookie(self):
        warnings.warn('check_for_test_cookie is deprecated; ensure your login '
                      'view is CSRF-protected.', DeprecationWarning)

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UsernameAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(label=_('Remember me'), required=False)
