from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import permission_events_view


def get_kwargs_factory(variable_name):
    def get_kwargs(context):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        content_type = ContentType.objects.get_for_model(
            context[variable_name]
        )
        return {
            'app_label': '"{}"'.format(content_type.app_label),
            'model': '"{}"'.format(content_type.model),
            'object_id': '{}.pk'.format(variable_name)
        }

    return get_kwargs


link_events_list = Link(
    icon='fa fa-list-ol', permissions=(permission_events_view,),
    text=_('Events'), view='events:events_list'
)
link_events_for_object = Link(
    icon='fa fa-list-ol', permissions=(permission_events_view,),
    text=_('Events'), view='events:events_for_object',
    kwargs=get_kwargs_factory('resolved_object')
)
