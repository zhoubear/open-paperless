from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Menu

menu_tags = Menu(
    icon='fa fa-tag', label=_('Tags'), name='tags menu'
)
