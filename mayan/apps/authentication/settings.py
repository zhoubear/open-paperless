from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

from .literals import DEFAULT_LOGIN_METHOD, DEFAULT_MAXIMUM_SESSION_LENGTH

namespace = Namespace(name='authentication', label=_('Authentication'))
setting_login_method = namespace.add_setting(
    global_name='AUTHENTICATION_LOGIN_METHOD', default=DEFAULT_LOGIN_METHOD,
    help_text=_(
        'Controls the mechanism used to authenticated user. Options are: '
        'username, email'
    )
)
setting_maximum_session_length = namespace.add_setting(
    global_name='AUTHENTICATION_MAXIMUM_SESSION_LENGTH',
    default=DEFAULT_MAXIMUM_SESSION_LENGTH, help_text=_(
        'Maximum time an user clicking the "Remember me" checkbox will '
        'remain logged in. Value is time in seconds.'
    )
)
