from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

KEY_TYPES = {
    'pub': _('Public'),
    'sec': _('Secret'),
}

KEY_TYPE_PUBLIC = 'pub'
KEY_TYPE_SECRET = 'sec'

KEY_TYPE_CHOICES = (
    (KEY_TYPE_PUBLIC, _('Public')),
    (KEY_TYPE_SECRET, _('Secret')),
)

KEY_CLASS_RSA = 'RSA'
KEY_CLASS_DSA = 'DSA'
KEY_CLASS_ELG = 'ELG-E'

KEY_PRIMARY_CLASSES = (
    ((KEY_CLASS_RSA), _('RSA')),
    ((KEY_CLASS_DSA), _('DSA')),
)

KEY_SECONDARY_CLASSES = (
    ((KEY_CLASS_RSA), _('RSA')),
    ((KEY_CLASS_ELG), _('Elgamal')),
)

KEYSERVER_DEFAULT_PORT = 11371

SIGNATURE_STATE_BAD = 'signature bad'
SIGNATURE_STATE_NONE = None
SIGNATURE_STATE_ERROR = 'signature error'
SIGNATURE_STATE_NO_PUBLIC_KEY = 'no public key'
SIGNATURE_STATE_GOOD = 'signature good'
SIGNATURE_STATE_VALID = 'signature valid'

SIGNATURE_STATES = {
    SIGNATURE_STATE_BAD: {
        'text': _('Bad signature.'),
    },
    SIGNATURE_STATE_NONE: {
        'text': _('Document not signed or invalid signature.'),
    },
    SIGNATURE_STATE_ERROR: {
        'text': _('Signature error.'),
    },
    SIGNATURE_STATE_NO_PUBLIC_KEY: {
        'text': _(
            'Document is signed but no public key is available for '
            'verification.'
        ),
    },
    SIGNATURE_STATE_GOOD: {
        'text': _('Document is signed, and signature is good.'),
    },
    SIGNATURE_STATE_VALID: {
        'text': _('Document is signed with a valid signature.'),
    },
}

ERROR_MSG_NEED_PASSPHRASE = 'NEED_PASSPHRASE'
ERROR_MSG_BAD_PASSPHRASE = 'BAD_PASSPHRASE'
ERROR_MSG_GOOD_PASSPHRASE = 'GOOD_PASSPHRASE'
OUTPUT_MESSAGE_CONTAINS_PRIVATE_KEY = 'Contains private key'
