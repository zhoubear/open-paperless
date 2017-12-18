from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import permission_statistics_view

# Translators: 'Queue' here is the verb, to queue a statistic to update
link_execute = Link(
    permissions=(permission_statistics_view,), text=_('Queue'),
    view='statistics:statistic_queue', args='resolved_object.slug'
)
link_view = Link(
    permissions=(permission_statistics_view,), text=_('View'),
    view='statistics:statistic_detail', args='resolved_object.slug'
)
link_namespace_details = Link(
    permissions=(permission_statistics_view,), text=_('Namespace details'),
    view='statistics:namespace_details', args='resolved_object.slug'
)
link_namespace_list = Link(
    permissions=(permission_statistics_view,), text=_('Namespace list'),
    view='statistics:namespace_list'
)
link_statistics = Link(
    icon='fa fa-sort-numeric-desc', permissions=(permission_statistics_view,),
    text=_('Statistics'), view='statistics:namespace_list'
)
