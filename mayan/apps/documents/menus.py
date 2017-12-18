from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Menu

menu_documents = Menu(
    icon='fa fa-file', label=_('Documents'), name='documents menu'
)
