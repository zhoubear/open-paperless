from __future__ import unicode_literals

import base64
from io import BytesIO
import os
import time
import urllib

from django.core.files import File
from django.utils.encoding import force_text, python_2_unicode_compatible

from converter import TransformationResize, converter_class


class PseudoFile(File):
    def __init__(self, file, name):
        self.name = name
        self.file = file
        self.file.seek(0, os.SEEK_END)
        self.size = self.file.tell()
        self.file.seek(0)


class SourceUploadedFile(File):
    def __init__(self, source, file, extra_data=None):
        self.file = file
        self.source = source
        self.extra_data = extra_data


class Attachment(File):
    def __init__(self, part, name):
        self.name = name
        self.file = PseudoFile(
            BytesIO(part.get_payload(decode=True)), name=name
        )


@python_2_unicode_compatible
class StagingFile(object):
    """
    Simple class to extend the File class to add preview capabilities
    files in a directory on a storage
    """
    def __init__(self, staging_folder, filename=None, encoded_filename=None):
        self.staging_folder = staging_folder
        if encoded_filename:
            self.encoded_filename = str(encoded_filename)
            self.filename = base64.urlsafe_b64decode(
                urllib.unquote_plus(self.encoded_filename)
            ).decode('utf8')
        else:
            self.filename = filename
            self.encoded_filename = base64.urlsafe_b64encode(
                filename.encode('utf8')
            )

    def __str__(self):
        return force_text(self.filename)

    def as_file(self):
        return File(
            file=open(self.get_full_path(), mode='rb'), name=self.filename
        )

    def get_date_time_created(self):
        return time.ctime(os.path.getctime(self.get_full_path()))

    def get_full_path(self):
        return os.path.join(self.staging_folder.folder_path, self.filename)

    def get_image(self, size=None, as_base64=False, transformations=None):
        converter = converter_class(file_object=open(self.get_full_path()))

        if size:
            converter.transform(
                transformation=TransformationResize(
                    **dict(zip(('width', 'height'), (size.split('x'))))
                )
            )

        # Interactive transformations
        for transformation in transformations:
            converter.transform(transformation=transformation)

        return converter.get_page(as_base64=as_base64)

    def delete(self):
        os.unlink(self.get_full_path())
