from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from actstream.models import Action, any_stream
from rest_framework import generics

from acls.models import AccessControlList
from rest_api.permissions import MayanPermission

from .classes import Event
from .permissions import permission_events_view
from .serializers import EventSerializer, EventTypeSerializer


class APIObjectEventListView(generics.ListAPIView):
    """
    Return a list of events for the specified object.
    """

    serializer_class = EventSerializer

    def get_object(self):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        try:
            return content_type.get_object_for_this_type(
                pk=self.kwargs['object_id']
            )
        except content_type.model_class().DoesNotExist:
            raise Http404

    def get_queryset(self):
        obj = self.get_object()

        AccessControlList.objects.check_access(
            permissions=permission_events_view, user=self.request.user,
            obj=obj
        )

        return any_stream(obj)


class APIEventTypeListView(generics.ListAPIView):
    """
    Returns a list of all the available event types.
    """

    serializer_class = EventTypeSerializer
    queryset = sorted(Event.all(), key=lambda event: event.name)


class APIEventListView(generics.ListAPIView):
    """
    Returns a list of all the available events.
    """

    mayan_view_permissions = {'GET': (permission_events_view,)}
    permission_classes = (MayanPermission,)
    queryset = Action.objects.all()
    serializer_class = EventSerializer
