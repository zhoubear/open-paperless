from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from dynamic_search.classes import SearchModel

from .permissions import permission_metadata_type_view

metadata_type_search = SearchModel(
    app_label='metadata', model_name='MetadataType',
    permission=permission_metadata_type_view,
    serializer_string='metadata.serializers.MetadataTypeSerializer'
)

metadata_type_search.add_model_field(
    field='name', label=_('Name')
)
metadata_type_search.add_model_field(
    field='label', label=_('Label')
)
metadata_type_search.add_model_field(
    field='default', label=_('Default')
)
metadata_type_search.add_model_field(
    field='lookup', label=_('Lookup')
)
metadata_type_search.add_model_field(
    field='validation', label=_('Validator')
)
metadata_type_search.add_model_field(
    field='parser', label=_('Parser')
)
