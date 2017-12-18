from __future__ import unicode_literals


class PermissionError(Exception):
    pass


class InvalidNamespace(PermissionError):
    pass
