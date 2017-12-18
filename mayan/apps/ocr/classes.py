from __future__ import unicode_literals

from converter import converter_class


class OCRBackendBase(object):
    def execute(self, file_object, language=None, transformations=None):
        self.language = language

        if not transformations:
            transformations = []

        self.converter = converter_class(file_object=file_object)

        for transformation in transformations:
            self.converter.transform(transformation=transformation)
