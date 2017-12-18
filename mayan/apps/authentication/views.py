from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import (
    login, password_change, password_reset, password_reset_confirm,
    password_reset_complete, password_reset_done
)
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from stronghold.decorators import public

from .forms import EmailAuthenticationForm, UsernameAuthenticationForm
from .settings import setting_login_method, setting_maximum_session_length


@public
def login_view(request):
    """
    Control how the use is to be authenticated, options are 'email' and
    'username'
    """
    kwargs = {'template_name': 'authentication/login.html'}

    if setting_login_method.value == 'email':
        kwargs['authentication_form'] = EmailAuthenticationForm
    else:
        kwargs['authentication_form'] = UsernameAuthenticationForm

    if not request.user.is_authenticated:
        extra_context = {
            'appearance_type': 'plain',
            REDIRECT_FIELD_NAME: resolve_url(settings.LOGIN_REDIRECT_URL)
        }

        result = login(request, extra_context=extra_context, **kwargs)
        if request.method == 'POST':
            form = kwargs['authentication_form'](request, data=request.POST)
            if form.is_valid():
                if form.cleaned_data['remember_me']:
                    request.session.set_expiry(
                        setting_maximum_session_length.value
                    )
                else:
                    request.session.set_expiry(0)
        return result
    else:
        return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))


def password_change_view(request):
    """
    Password change wrapper for better control
    """
    extra_context = {'title': _('Current user password change')}

    return password_change(
        request, extra_context=extra_context,
        template_name='appearance/generic_form.html',
        post_change_redirect=reverse('authentication:password_change_done'),
    )


def password_change_done(request):
    """
    View called when the new user password has been accepted
    """
    messages.success(
        request, _('Your password has been successfully changed.')
    )
    return redirect('common:current_user_details')


@public
def password_reset_complete_view(request):
    extra_context = {
        'appearance_type': 'plain'
    }

    return password_reset_complete(
        request, extra_context=extra_context,
        template_name='authentication/password_reset_complete.html'
    )


@public
def password_reset_confirm_view(request, uidb64=None, token=None):
    extra_context = {
        'appearance_type': 'plain'
    }

    return password_reset_confirm(
        request, extra_context=extra_context,
        template_name='authentication/password_reset_confirm.html',
        post_reset_redirect=reverse(
            'authentication:password_reset_complete_view'
        ), uidb64=uidb64, token=token
    )


@public
def password_reset_done_view(request):
    extra_context = {
        'appearance_type': 'plain'
    }

    return password_reset_done(
        request, extra_context=extra_context,
        template_name='authentication/password_reset_done.html'
    )


@public
def password_reset_view(request):
    extra_context = {
        'appearance_type': 'plain'
    }

    return password_reset(
        request, extra_context=extra_context,
        email_template_name='authentication/password_reset_email.html',
        extra_email_context={
            'project_title': settings.PROJECT_TITLE,
            'project_website': settings.PROJECT_WEBSITE,
            'project_copyright': settings.PROJECT_COPYRIGHT,
            'project_license': settings.PROJECT_LICENSE,
        }, subject_template_name='authentication/password_reset_subject.txt',
        template_name='authentication/password_reset_form.html',
        post_reset_redirect=reverse(
            'authentication:password_reset_done_view'
        )
    )
