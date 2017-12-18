from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext


class DocumentCheckoutError(Exception):
    """
    Base checkout exception
    """
    pass


class DocumentNotCheckedOut(DocumentCheckoutError):
    """
    Raised when trying to checkin a document that is not checkedout
    """
    pass


@python_2_unicode_compatible
class DocumentAlreadyCheckedOut(DocumentCheckoutError):
    """
    Raised when trying to checkout an already checkedout document
    """
    def __str__(self):
        return ugettext('Document already checked out.')


class NewDocumentVersionNotAllowed(DocumentCheckoutError):
    """
    Uploading new versions for this document is not allowed
    """
    pass
