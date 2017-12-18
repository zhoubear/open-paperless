from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from document_states.classes import WorkflowAction
from permissions.classes import Permission
from permissions.models import Role

from .classes import ModelPermission
from .permissions import permission_acl_edit

__all__ = ('GrantAccessAction', 'RevokeAccessAction')
logger = logging.getLogger(__name__)


class GrantAccessAction(WorkflowAction):
    fields = {
        'content_type': {
            'label': _('Object type'),
            'class': 'django.forms.ModelChoiceField', 'kwargs': {
                'help_text': _(
                    'Type of the object for which the access will be modified.'
                ),
                'queryset': ContentType.objects.none(),
                'required': True
            }
        }, 'object_id': {
            'label': _('Object ID'),
            'class': 'django.forms.IntegerField', 'kwargs': {
                'help_text': _(
                    'Numeric identifier of the object for which the access '
                    'will be modified.'
                ), 'required': True
            }
        }, 'roles': {
            'label': _('Roles'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _('Roles whose access will be modified.'),
                'queryset': Role.objects.all(), 'required': True
            }
        }, 'permissions': {
            'label': _('Permissions'),
            'class': 'django.forms.MultipleChoiceField', 'kwargs': {
                'help_text': _(
                    'Permissions to grant/revoke to/from the role for the '
                    'object selected above.'
                ), 'choices': (),
                'required': True
            }
        }
    }
    field_order = ('content_type', 'object_id', 'roles', 'permissions')
    label = _('Grant access')
    widgets = {
        'roles': {
            'class': 'django.forms.widgets.SelectMultiple', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        },
        'permissions': {
            'class': 'django.forms.widgets.SelectMultiple', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        }
    }

    @classmethod
    def clean(cls, request, form_data=None):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        content_type = ContentType.objects.get(
            pk=int(form_data['action_data']['content_type'])
        )
        obj = content_type.get_object_for_this_type(
            pk=int(form_data['action_data']['object_id'])
        )

        try:
            AccessControlList.objects.check_access(
                permissions=permission_acl_edit, user=request.user, obj=obj
            )
        except Exception as exception:
            raise ValidationError(exception)
        else:
            return form_data

    def get_form_schema(self, *args, **kwargs):
        self.fields['content_type']['kwargs']['queryset'] = ModelPermission.get_classes(as_content_type=True)
        self.fields['permissions']['kwargs']['choices'] = Permission.all(as_choices=True)
        return super(GrantAccessAction, self).get_form_schema(*args, **kwargs)

    def get_execute_data(self):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        content_type = ContentType.objects.get(
            pk=self.form_data['content_type']
        )
        self.obj = content_type.get_object_for_this_type(
            pk=self.form_data['object_id']
        )
        self.roles = Role.objects.filter(pk__in=self.form_data['roles'])
        self.permissions = [Permission.get(pk=permission, proxy_only=True) for permission in self.form_data['permissions']]

    def execute(self, context):
        self.get_execute_data()

        for role in self.roles:
            for permission in self.permissions:
                AccessControlList.objects.grant(
                    obj=self.obj, permission=permission, role=role
                )


class RevokeAccessAction(GrantAccessAction):
    label = _('Revoke access')

    def execute(self, context):
        self.get_execute_data()

        for role in self.roles:
            for permission in self.permissions:
                AccessControlList.objects.revoke(
                    obj=self.obj, permission=permission, role=role
                )
