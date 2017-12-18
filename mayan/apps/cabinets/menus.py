from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Menu

menu_cabinets = Menu(
    icon='fa fa-columns', label=_('Cabinets'), name='cabinets menu'
)
