from __future__ import unicode_literals

import logging
import os

from django.db import models

from common.utils import mkstemp
from django_gpg.exceptions import DecryptionError
from django_gpg.models import Key
from documents.models import DocumentVersion

logger = logging.getLogger(__name__)


class EmbeddedSignatureManager(models.Manager):
    def open_signed(self, file_object, document_version):
        for signature in self.filter(document_version=document_version):
            try:
                return self.open_signed(
                    file_object=Key.objects.decrypt_file(
                        file_object=file_object
                    ), document_version=document_version
                )
            except DecryptionError:
                file_object.seek(0)
                return file_object
        else:
            return file_object

    def unsigned_document_versions(self):
        return DocumentVersion.objects.exclude(
            pk__in=self.values('document_version')
        )

    def sign_document_version(self, document_version, key, passphrase=None, user=None):
        temporary_file_object, temporary_filename = mkstemp()

        try:
            with document_version.open() as file_object:
                key.sign_file(
                    binary=True, file_object=file_object,
                    output=temporary_filename, passphrase=passphrase
                )
        except Exception:
            raise
        else:
            with open(temporary_filename) as file_object:
                new_version = document_version.document.new_version(
                    file_object=file_object, _user=user
                )
        finally:
            os.unlink(temporary_filename)

        return new_version
