from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_object, menu_sidebar

from navigation import SourceColumn

from .links import (
    link_transformation_create, link_transformation_delete,
    link_transformation_edit
)
from .licenses import *  # NOQA


class ConverterApp(MayanAppConfig):
    has_tests = True
    name = 'converter'
    verbose_name = _('Converter')

    def ready(self):
        super(ConverterApp, self).ready()

        Transformation = self.get_model('Transformation')

        SourceColumn(source=Transformation, label=_('Order'), attribute='order')
        SourceColumn(
            source=Transformation, label=_('Transformation'),
            func=lambda context: force_text(context['object'])
        )
        SourceColumn(
            source=Transformation, label=_('Arguments'), attribute='arguments'
        )

        menu_object.bind_links(
            links=(link_transformation_edit, link_transformation_delete),
            sources=(Transformation,)
        )
        menu_sidebar.bind_links(
            links=(link_transformation_create,), sources=(Transformation,)
        )
        menu_sidebar.bind_links(
            links=(link_transformation_create,),
            sources=(
                'converter:transformation_create',
                'converter:transformation_list'
            )
        )
