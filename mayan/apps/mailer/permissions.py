from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('mailing', _('Mailing'))

permission_mailing_link = namespace.add_permission(
    name='mail_link', label=_('Send document link via email')
)
permission_mailing_send_document = namespace.add_permission(
    name='mail_document', label=_('Send document via email')
)
permission_view_error_log = namespace.add_permission(
    name='view_error_log', label=_('View system mailing error log')
)
permission_user_mailer_create = namespace.add_permission(
    name='user_mailer_create', label=_('Create a mailing profile')
)
permission_user_mailer_delete = namespace.add_permission(
    name='user_mailer_delete', label=_('Delete a mailing profile')
)
permission_user_mailer_edit = namespace.add_permission(
    name='user_mailer_edit', label=_('Edit a mailing profile')
)
permission_user_mailer_view = namespace.add_permission(
    name='user_mailer_view', label=_('View a mailing profile')
)
permission_user_mailer_use = namespace.add_permission(
    name='user_mailer_use', label=_('Use a mailing profile')
)
