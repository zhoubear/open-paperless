from __future__ import unicode_literals


class BaseCommonException(Exception):
    """
    Base exception for the common app
    """
    pass


class NotLatestVersion(BaseCommonException):
    """
    The installed version is not the latest available version
    """
    def __init__(self, upstream_version):
        self.upstream_version = upstream_version
