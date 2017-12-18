from __future__ import absolute_import, unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext, ugettext_lazy as _

from common.utils import return_attrib
from permissions import Permission
from permissions.models import StoredPermission

from .exceptions import PermissionNotValidForClass
from .classes import ModelPermission

logger = logging.getLogger(__name__)


class AccessControlListManager(models.Manager):
    """
    Implement a 3 tier permission system, involving a permissions, an actor
    and an object
    """
    def check_access(self, permissions, user, obj, related=None):
        if user.is_superuser or user.is_staff:
            logger.debug(
                'Permissions "%s" on "%s" granted to user "%s" as superuser '
                'or staff', permissions, obj, user
            )
            return True

        try:
            return Permission.check_permissions(
                requester=user, permissions=permissions
            )
        except PermissionDenied:
            try:
                stored_permissions = [
                    permission.stored_permission for permission in permissions
                ]
            except TypeError:
                # Not a list of permissions, just one
                stored_permissions = (permissions.stored_permission,)

            if related:
                obj = return_attrib(obj, related)

            try:
                parent_accessor = ModelPermission.get_inheritance(
                    model=obj._meta.model
                )
            except AttributeError:
                # AttributeError means non model objects: ie Statistics
                # These can't have ACLs so we raise PermissionDenied
                raise PermissionDenied(_('Insufficient access for: %s') % obj)
            except KeyError:
                pass
            else:
                try:
                    return self.check_access(
                        obj=getattr(obj, parent_accessor),
                        permissions=permissions, user=user
                    )
                except PermissionDenied:
                    pass

            user_roles = []
            for group in user.groups.all():
                for role in group.roles.all():
                    if set(stored_permissions).intersection(set(self.get_inherited_permissions(role=role, obj=obj))):
                        logger.debug(
                            'Permissions "%s" on "%s" granted to user "%s" through role "%s" via inherited ACL',
                            permissions, obj, user, role
                        )
                        return True

                    user_roles.append(role)

            if not self.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk, permissions__in=stored_permissions, role__in=user_roles).exists():
                logger.debug(
                    'Permissions "%s" on "%s" denied for user "%s"',
                    permissions, obj, user
                )
                raise PermissionDenied(ugettext('Insufficient access for: %s') % obj)

            logger.debug(
                'Permissions "%s" on "%s" granted to user "%s" through roles "%s" by direct ACL',
                permissions, obj, user, user_roles
            )

    def filter_by_access(self, permission, user, queryset):
        if user.is_superuser or user.is_staff:
            logger.debug('Unfiltered queryset returned to user "%s" as superuser or staff',
                         user)
            return queryset

        try:
            Permission.check_permissions(
                requester=user, permissions=(permission,)
            )
        except PermissionDenied:
            user_roles = []
            for group in user.groups.all():
                for role in group.roles.all():
                    user_roles.append(role)

            try:
                parent_accessor = ModelPermission.get_inheritance(
                    model=queryset.model
                )
            except KeyError:
                parent_acl_query = Q()
            else:
                instance = queryset.first()
                if instance:
                    parent_object = getattr(instance, parent_accessor)

                    try:
                        # Try to see if parent_object is a function
                        parent_object()
                    except TypeError:
                        # Is not a function, try it as a field
                        parent_content_type = ContentType.objects.get_for_model(
                            parent_object
                        )
                        parent_queryset = self.filter(
                            content_type=parent_content_type, role__in=user_roles,
                            permissions=permission.stored_permission
                        )
                        parent_acl_query = Q(
                            **{
                                '{}__pk__in'.format(
                                    parent_accessor
                                ): parent_queryset.values_list(
                                    'object_id', flat=True
                                )
                            }
                        )
                    else:
                        # Is a function. Can't perform Q object filtering.
                        # Perform iterative filtering.
                        result = []
                        for entry in queryset:
                            try:
                                self.check_access(permissions=permission, user=user, obj=entry)
                            except PermissionDenied:
                                pass
                            else:
                                result.append(entry.pk)

                        return queryset.filter(pk__in=result)
                else:
                    parent_acl_query = Q()

            # Directly granted access
            content_type = ContentType.objects.get_for_model(queryset.model)
            acl_query = Q(pk__in=self.filter(
                content_type=content_type, role__in=user_roles,
                permissions=permission.stored_permission
            ).values_list('object_id', flat=True))
            logger.debug(
                'Filtered queryset returned to user "%s" based on roles "%s"',
                user, user_roles
            )

            return queryset.filter(parent_acl_query | acl_query)
        else:
            return queryset

    def get_inherited_permissions(self, role, obj):
        try:
            instance = obj.first()
        except AttributeError:
            instance = obj
        else:
            if not instance:
                return StoredPermission.objects.none()

        try:
            parent_accessor = ModelPermission.get_inheritance(type(instance))
        except KeyError:
            return StoredPermission.objects.none()
        else:
            parent_object = return_attrib(instance, parent_accessor)
            content_type = ContentType.objects.get_for_model(parent_object)
            try:
                return self.get(
                    role=role, content_type=content_type,
                    object_id=parent_object.pk
                ).permissions.all()
            except self.model.DoesNotExist:
                return StoredPermission.objects.none()

    def grant(self, permission, role, obj):
        class_permissions = ModelPermission.get_for_class(klass=obj.__class__)
        if permission not in class_permissions:
            raise PermissionNotValidForClass

        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.add(permission.stored_permission)

    def revoke(self, permission, role, obj):
        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.remove(permission.stored_permission)

        if acl.permissions.count() == 0:
            acl.delete()
