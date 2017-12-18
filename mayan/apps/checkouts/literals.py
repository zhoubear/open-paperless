from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

CHECK_EXPIRED_CHECK_OUTS_INTERVAL = 60  # Lowest check out expiration allowed
CHECKOUT_EXPIRATION_LOCK_EXPIRE = 50

STATE_CHECKED_OUT = 'checkedout'
STATE_CHECKED_IN = 'checkedin'

STATE_LABELS = {
    STATE_CHECKED_OUT: _('Checked out'),
    STATE_CHECKED_IN: _('Checked in/available'),
}
