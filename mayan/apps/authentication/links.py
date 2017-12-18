from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link


def has_usable_password(context):
    return context['request'].user.has_usable_password


link_logout = Link(
    icon='fa fa-sign-out', text=_('Logout'), view='authentication:logout_view'
)
link_password_change = Link(
    condition=has_usable_password, icon='fa fa-key', text=_('Change password'),
    view='authentication:password_change_view'
)
