from __future__ import unicode_literals


class ConvertError(Exception):
    """
    Base exception for all coverter app exceptions
    """
    pass


class UnknownFileFormat(ConvertError):
    """
    Raised when the converter backend can't understand a file
    """
    pass


class UnkownConvertError(ConvertError):
    """
    Raised when an error is found but there is no disernible way to
    identify the kind of error
    """
    pass


class OfficeConversionError(ConvertError):
    pass


class InvalidOfficeFormat(ConvertError):
    pass


class PageCountError(ConvertError):
    pass
