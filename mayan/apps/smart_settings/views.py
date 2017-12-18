from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from common.views import SingleObjectListView

from .classes import Namespace
from .permissions import permission_settings_view


class NamespaceListView(SingleObjectListView):
    extra_context = {
        'hide_link': True,
        'title': _('Setting namespaces'),
    }
    view_permission = permission_settings_view

    def get_object_list(self):
        return Namespace.get_all()


class NamespaceDetailView(SingleObjectListView):
    view_permission = permission_settings_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Settings in namespace: %s') % self.get_namespace(),
        }

    def get_namespace(self):
        try:
            return Namespace.get(self.kwargs['namespace_name'])
        except KeyError:
            raise Http404(
                _('Namespace: %s, not found') % self.kwargs['namespace_name']
            )

    def get_object_list(self):
        return self.get_namespace().settings
