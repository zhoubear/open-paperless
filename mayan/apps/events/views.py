from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from actstream.models import Action, any_stream

from acls.models import AccessControlList
from common.utils import encapsulate
from common.views import SingleObjectListView

from .classes import Event
from .permissions import permission_events_view
from .widgets import event_object_link


class EventListView(SingleObjectListView):
    view_permission = permission_events_view

    def get_extra_context(self):
        return {
            'extra_columns': (
                {
                    'name': _('Target'),
                    'attribute': encapsulate(
                        lambda entry: event_object_link(entry)
                    )
                },
            ),
            'hide_object': True,
            'title': _('Events'),
        }

    def get_object_list(self):
        return Action.objects.all()


class ObjectEventListView(EventListView):
    view_permissions = None

    def dispatch(self, request, *args, **kwargs):
        self.object_content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        try:
            self.content_object = self.object_content_type.get_object_for_this_type(
                pk=self.kwargs['object_id']
            )
        except self.object_content_type.model_class().DoesNotExist:
            raise Http404

        AccessControlList.objects.check_access(
            permissions=permission_events_view, user=request.user,
            obj=self.content_object
        )

        return super(
            ObjectEventListView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.content_object,
            'title': _('Events for: %s') % self.content_object,
        }

    def get_object_list(self):
        return any_stream(self.content_object)


class VerbEventListView(SingleObjectListView):
    def get_extra_context(self):
        return {
            'extra_columns': (
                {
                    'name': _('Target'),
                    'attribute': encapsulate(
                        lambda entry: event_object_link(entry)
                    )
                },
            ),
            'hide_object': True,
            'title': _(
                'Events of type: %s'
            ) % Event.get_label(self.kwargs['verb']),
        }

    def get_object_list(self):
        return Action.objects.filter(verb=self.kwargs['verb'])
