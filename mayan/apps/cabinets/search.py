from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from dynamic_search.classes import SearchModel

from .permissions import permission_cabinet_view

cabinet_search = SearchModel(
    app_label='cabinets', model_name='Cabinet',
    permission=permission_cabinet_view,
    serializer_string='cabinets.serializers.CabinetSerializer'
)

cabinet_search.add_model_field(
    field='label', label=_('Label')
)
