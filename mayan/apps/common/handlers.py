from __future__ import unicode_literals

from django.apps import apps
from django.conf import settings
from django.core import management
from django.utils import timezone, translation


def handler_pre_initial_setup(sender, **kwargs):
    management.call_command('migrate', interactive=False)


def handler_pre_upgrade(sender, **kwargs):
    management.call_command('migrate', fake_initial=True, interactive=False)
    management.call_command('purgeperiodictasks', interactive=False)


def user_locale_profile_session_config(sender, request, user, **kwargs):
    UserLocaleProfile = apps.get_model(
        app_label='common', model_name='UserLocaleProfile'
    )

    user_locale_profile, created = UserLocaleProfile.objects.get_or_create(
        user=user
    )

    if not created and user_locale_profile.timezone and user_locale_profile.language:
        # Don't try to set locale preferences for new users or existing users
        # that have not set any preferences
        timezone.activate(user_locale_profile.timezone)
        translation.activate(user_locale_profile.language)

        if hasattr(request, 'session'):
            request.session[
                translation.LANGUAGE_SESSION_KEY
            ] = user_locale_profile.language
            request.session[
                settings.TIMEZONE_SESSION_KEY
            ] = user_locale_profile.timezone
        else:
            request.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, user_locale_profile.language
            )
            request.set_cookie(
                settings.TIMEZONE_COOKIE_NAME, user_locale_profile.timezone
            )


def user_locale_profile_create(sender, instance, created, **kwargs):
    UserLocaleProfile = apps.get_model(
        app_label='common', model_name='UserLocaleProfile'
    )

    if created:
        UserLocaleProfile.objects.create(user=instance)
