from __future__ import absolute_import, unicode_literals

from rest_framework import generics

from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Key
from .permissions import (
    permission_key_delete, permission_key_upload, permission_key_view
)
from .serializers import KeySerializer


class APIKeyListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_key_view,),
        'POST': (permission_key_upload,)
    }
    permission_classes = (MayanPermission,)
    queryset = Key.objects.all()
    serializer_class = KeySerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the keys.
        """
        return super(APIKeyListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Upload a new key.
        """
        return super(APIKeyListView, self).post(*args, **kwargs)


class APIKeyView(generics.RetrieveDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_key_delete,),
        'GET': (permission_key_view,),
    }
    queryset = Key.objects.all()
    serializer_class = KeySerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected key.
        """

        return super(APIKeyView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected key.
        """

        return super(APIKeyView, self).get(*args, **kwargs)
