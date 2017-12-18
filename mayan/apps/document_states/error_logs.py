from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common.classes import ErrorLogNamespace

error_log_state_actions = ErrorLogNamespace(
    name='workflow_state_actions', label=_('Workflow state actions')
)
