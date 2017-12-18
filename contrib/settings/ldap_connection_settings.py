from __future__ import absolute_import

import ldap
from django_auth_ldap.config import LDAPSearch

from .base import *
from django.conf import settings
from django.contrib.auth import get_user_model

SECRET_KEY = '<your secret key>'

# makes sure this works in Active Directory
ldap.set_option(ldap.OPT_REFERRALS, 0)

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

LDAP_USER_AUTO_CREATION = "False"
LDAP_URL = "ldap://<your ldap server IP>:389/"
LDAP_BASE_DN = "dc=paramatrix,dc=co,dc=in"
LDAP_ADDITIONAL_USER_DN = "dc=people"
LDAP_ADMIN_DN = ""
LDAP_PASSWORD = ""

AUTH_LDAP_SERVER_URI = LDAP_URL
AUTH_LDAP_BIND_DN = LDAP_ADMIN_DN
AUTH_LDAP_BIND_PASSWORD = LDAP_PASSWORD


AUTH_LDAP_USER_SEARCH = LDAPSearch('%s,%s'%(LDAP_ADDITIONAL_USER_DN, LDAP_BASE_DN), ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_USER_ATTR_MAP = {
                           "first_name": "cn",
                           "last_name": "sn",
			   "email": "mail"
                          }

AUTHENTICATION_BACKENDS = (
'django_auth_ldap.backend.LDAPBackend',
'mayan.settings.settings_local.EmailOrUsernameModelBackend',
)

class EmailOrUsernameModelBackend(object):
    """
    This is a ModelBacked that allows authentication with either a username or an email address.

    """
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None
