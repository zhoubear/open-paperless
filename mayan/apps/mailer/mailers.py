from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .classes import MailerBackend

__all__ = ('DjangoSMTP', 'DjangoFileBased')


class DjangoSMTP(MailerBackend):
    class_path = 'django.core.mail.backends.smtp.EmailBackend'
    fields = {
        'host': {
            'label': _('Host'),
            'class': 'django.forms.CharField', 'default': 'localhost',
            'help_text': _('The host to use for sending email.'),
            'kwargs': {
                'max_length': 48
            }, 'required': False
        }, 'port': {
            'label': _('Port'),
            'class': 'django.forms.IntegerField', 'default': 25,
            'help_text': _('Port to use for the SMTP server.'),
            'required': False
        }, 'use_tls': {
            'label': _('Use TLS'),
            'class': 'django.forms.BooleanField', 'default': False,
            'help_text': _(
                'Whether to use a TLS (secure) connection when talking to '
                'the SMTP server. This is used for explicit TLS connections, '
                'generally on port 587.'
            ), 'required': False
        }, 'use_ssl': {
            'label': _('Use SSL'),
            'class': 'django.forms.BooleanField', 'default': False,
            'help_text': _(
                'Whether to use an implicit TLS (secure) connection when '
                'talking to the SMTP server. In most email documentation '
                'this type of TLS connection is referred to as SSL. It is '
                'generally used on port 465. If you are experiencing '
                'problems, see the explicit TLS setting "Use TLS". Note '
                'that "Use TLS" and "Use SSL" are mutually exclusive, '
                'so only set one of those settings to True.'
            ), 'required': False
        }, 'user': {
            'label': _('Username'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                'Username to use for the SMTP server. If empty, '
                'authentication won\'t attempted.'
            ), 'kwargs': {
                'max_length': 48
            }, 'required': False
        }, 'password': {
            'label': _('Password'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                'Password to use for the SMTP server. This setting is used '
                'in conjunction with the username when authenticating to '
                'the SMTP server. If either of these settings is empty, '
                'authentication won\'t be attempted.'
            ), 'kwargs': {
                'max_length': 48
            }, 'required': False
        },
    }
    field_order = ('host', 'port', 'use_tls', 'use_ssl', 'user', 'password')
    widgets = {
        'password': {
            'class': 'django.forms.widgets.PasswordInput',
            'kwargs': {
                'render_value': True
            }
        }
    }
    label = _('Django SMTP backend')


class DjangoFileBased(MailerBackend):
    class_path = 'django.core.mail.backends.filebased.EmailBackend'
    fields = {
        'file_path': {
            'label': _('File path'),
            'class': 'django.forms.CharField', 'kwargs': {
                'max_length': 48
            }
        },
    }
    label = _('Django file based backend')
