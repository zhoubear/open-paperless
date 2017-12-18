from __future__ import absolute_import, unicode_literals

from rest_framework import generics

from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Message
from .permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)
from .serializers import MessageSerializer


class APIMessageListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_message_view,)}
    mayan_view_permissions = {'POST': (permission_message_create,)}
    permission_classes = (MayanPermission,)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the messages.
        """

        return super(APIMessageListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a new message.
        """

        return super(APIMessageListView, self).post(*args, **kwargs)


class APIMessageView(generics.RetrieveUpdateDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_message_delete,),
        'GET': (permission_message_view,),
        'PATCH': (permission_message_edit,),
        'PUT': (permission_message_edit,)
    }
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected message.
        """

        return super(APIMessageView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected message.
        """

        return super(APIMessageView, self).get(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Edit the selected message.
        """

        return super(APIMessageView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected message.
        """

        return super(APIMessageView, self).put(*args, **kwargs)
