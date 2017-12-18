from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

WORKFLOW_ACTION_ON_ENTRY = 1
WORKFLOW_ACTION_ON_EXIT = 2

WORKFLOW_ACTION_WHEN_CHOICES = (
    (WORKFLOW_ACTION_ON_ENTRY, _('On entry')),
    (WORKFLOW_ACTION_ON_EXIT, _('On exit')),
)
