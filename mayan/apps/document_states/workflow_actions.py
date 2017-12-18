from __future__ import absolute_import, unicode_literals

import logging
import json

import requests

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from .classes import WorkflowAction
from .exceptions import WorkflowStateActionError

__all__ = ('HTTPPostAction',)
logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 4  # 4 seconds


class HTTPPostAction(WorkflowAction):
    fields = {
        'url': {
            'label': _('URL'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Can be an IP address, a domain or a template. Templates '
                    'receive the workflow log entry instance as part of '
                    'their context via the variable "entry_log". '
                    'The "entry_log" in turn provides the '
                    '"workflow_instance", "datetime", "transition", "user", '
                    'and "comment" attributes.'
                ),
                'required': True
            },
        }, 'timeout': {
            'label': _('Timeout'),
            'class': 'django.forms.IntegerField', 'default': DEFAULT_TIMEOUT,
            'help_text': _('Time in seconds to wait for a response.'),
            'required': True

        }, 'payload': {
            'label': _('Payload'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'A JSON document to include in the request. Can also be '
                    'a template that return a JSON document. Templates '
                    'receive the workflow log entry instance as part of '
                    'their context via the variable "entry_log". '
                    'The "entry_log" in turn provides the '
                    '"workflow_instance", "datetime", "transition", "user", '
                    'and "comment" attributes.'
                ), 'required': False
            }

        },
    }
    field_order = ('url', 'timeout', 'payload')
    label = _('Perform a POST request')
    widgets = {
        'payload': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {'rows': '10'},
            }
        }
    }

    def execute(self, context):
        self.url = self.form_data.get('url')
        self.payload = self.form_data.get('payload')

        try:
            url = Template(self.url).render(
                context=Context(context)
            )
        except Exception as exception:
            raise WorkflowStateActionError(
                _('URL template error: %s') % exception
            )

        logger.debug('URL template result: %s', url)

        try:
            result = Template(self.payload or '{}').render(
                context=Context(context)
            )
        except Exception as exception:
            raise WorkflowStateActionError(
                _('Payload template error: %s') % exception
            )

        logger.debug('payload template result: %s', result)

        try:
            payload = json.loads(result, strict=False)
        except Exception as exception:
            raise WorkflowStateActionError(
                _('Payload JSON error: %s') % exception
            )

        logger.debug('payload json result: %s', payload)

        requests.post(url=url, data=payload, timeout=self.form_data['timeout'])
