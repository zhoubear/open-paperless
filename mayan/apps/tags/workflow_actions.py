from __future__ import absolute_import, unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from document_states.classes import WorkflowAction
from tags.models import Tag
from tags.permissions import permission_tag_attach, permission_tag_remove

__all__ = ('AttachTagAction', 'RemoveTagAction')
logger = logging.getLogger(__name__)


class AttachTagAction(WorkflowAction):
    fields = {
        'tags': {
            'label': _('Tags'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _('Tags to attach to the document'),
                'queryset': Tag.objects.none(), 'required': False
            }
        },
    }
    label = _('Attach tag')
    widgets = {
        'tags': {
            'class': 'tags.widgets.TagFormWidget', 'kwargs': {
                'attrs': {'class': 'select2-tags'},
                'queryset': Tag.objects.none()
            }
        }
    }
    permission = permission_tag_attach

    def get_form_schema(self, request):
        user = request.user
        logger.debug('user: %s', user)

        queryset = AccessControlList.objects.filter_by_access(
            self.permission, user, queryset=Tag.objects.all()
        )

        self.fields['tags']['kwargs']['queryset'] = queryset
        self.widgets['tags']['kwargs']['queryset'] = queryset

        return {
            'fields': self.fields,
            'widgets': self.widgets
        }

    def get_tags(self):
        return Tag.objects.filter(pk__in=self.form_data.get('tags', ()))

    def execute(self, context):
        for tag in self.get_tags():
            tag.attach_to(
                document=context['entry_log'].workflow_instance.document
            )


class RemoveTagAction(AttachTagAction):
    fields = {
        'tags': {
            'label': _('Tags'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _('Tags to remove from the document'),
                'queryset': Tag.objects.none(), 'required': False
            }
        },
    }
    label = _('Remove tag')
    permission = permission_tag_remove

    def execute(self, context):
        for tag in self.get_tags():
            tag.remove_from(
                document=context['entry_log'].workflow_instance.document
            )
