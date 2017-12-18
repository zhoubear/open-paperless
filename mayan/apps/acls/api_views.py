from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from rest_framework import generics

from permissions import Permission

from .models import AccessControlList
from .permissions import permission_acl_edit, permission_acl_view
from .serializers import (
    AccessControlListPermissionSerializer, AccessControlListSerializer,
    WritableAccessControlListPermissionSerializer,
    WritableAccessControlListSerializer
)


class APIObjectACLListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns a list of all the object's access control lists
        """

        return super(APIObjectACLListView, self).get(*args, **kwargs)

    def get_content_object(self):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        content_object = get_object_or_404(
            content_type.model_class(), pk=self.kwargs['object_pk']
        )

        if self.request.method == 'GET':
            permission_required = permission_acl_view
        else:
            permission_required = permission_acl_edit

        try:
            Permission.check_permissions(
                self.request.user, permissions=(permission_required,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_required, self.request.user, content_object
            )

        return content_object

    def get_queryset(self):
        return self.get_content_object().acls.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """

        return {
            'content_object': self.get_content_object(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AccessControlListSerializer
        else:
            return WritableAccessControlListSerializer

    def post(self, *args, **kwargs):
        """
        Create a new access control list for the selected object.
        """

        return super(APIObjectACLListView, self).post(*args, **kwargs)


class APIObjectACLView(generics.RetrieveDestroyAPIView):
    serializer_class = AccessControlListSerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected access control list.
        """

        return super(APIObjectACLView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected access control list.
        """

        return super(APIObjectACLView, self).get(*args, **kwargs)

    def get_content_object(self):
        if self.request.method == 'GET':
            permission_required = permission_acl_view
        else:
            permission_required = permission_acl_edit

        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        content_object = get_object_or_404(
            content_type.model_class(), pk=self.kwargs['object_pk']
        )

        try:
            Permission.check_permissions(
                self.request.user, permissions=(permission_required,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_required, self.request.user, content_object
            )

        return content_object

    def get_queryset(self):
        return self.get_content_object().acls.all()


class APIObjectACLPermissionListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns the access control list permission list.
        """

        return super(
            APIObjectACLPermissionListView, self
        ).get(*args, **kwargs)

    def get_acl(self):
        return get_object_or_404(
            self.get_content_object().acls, pk=self.kwargs['pk']
        )

    def get_content_object(self):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        content_object = get_object_or_404(
            content_type.model_class(), pk=self.kwargs['object_pk']
        )

        try:
            Permission.check_permissions(
                self.request.user, permissions=(permission_acl_view,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_acl_view, self.request.user, content_object
            )

        return content_object

    def get_queryset(self):
        return self.get_acl().permissions.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AccessControlListPermissionSerializer
        else:
            return WritableAccessControlListPermissionSerializer

    def get_serializer_context(self):
        return {
            'acl': self.get_acl(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def post(self, *args, **kwargs):
        """
        Add a new permission to the selected access control list.
        """

        return super(
            APIObjectACLPermissionListView, self
        ).post(*args, **kwargs)


class APIObjectACLPermissionView(generics.RetrieveDestroyAPIView):
    lookup_url_kwarg = 'permission_pk'
    serializer_class = AccessControlListPermissionSerializer

    def delete(self, *args, **kwargs):
        """
        Remove the permission from the selected access control list.
        """

        return super(
            APIObjectACLPermissionView, self
        ).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected access control list permission.
        """

        return super(
            APIObjectACLPermissionView, self
        ).get(*args, **kwargs)

    def get_acl(self):
        return get_object_or_404(
            self.get_content_object().acls, pk=self.kwargs['pk']
        )

    def get_content_object(self):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        content_object = get_object_or_404(
            content_type.model_class(), pk=self.kwargs['object_pk']
        )

        try:
            Permission.check_permissions(
                self.request.user, permissions=(permission_acl_view,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_acl_view, self.request.user, content_object
            )

        return content_object

    def get_queryset(self):
        return self.get_acl().permissions.all()

    def get_serializer_context(self):
        return {
            'acl': self.get_acl(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }
