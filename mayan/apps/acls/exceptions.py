from __future__ import unicode_literals


class ACLsBaseException(Exception):
    """
    Base exception for the acls app
    """
    pass


class PermissionNotValidForClass(ACLsBaseException):
    """
    The permission is not one that has been registered for a class using the
    ModelPermission class.
    """
    pass
