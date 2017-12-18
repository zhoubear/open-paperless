from __future__ import unicode_literals

from common.classes import PropertyHelper


class DocumentMetadataHelper(PropertyHelper):
    @staticmethod
    @property
    def constructor(*args, **kwargs):
        return DocumentMetadataHelper(*args, **kwargs)

    def get_result(self, name):
        return self.instance.metadata.get(metadata_type__name=name).value


class MetadataLookup(object):
    _registry = []

    @classmethod
    def get_as_context(cls):
        result = {}
        for entry in cls._registry:
            try:
                result[entry.name] = entry.value()
            except TypeError:
                result[entry.name] = entry.value

        return result

    @classmethod
    def get_as_help_text(cls):
        result = []
        for entry in cls._registry:
            result.append(
                '{{{{ {0} }}}} = "{1}"'.format(entry.name, entry.description)
            )

        return ' '.join(result)

    def __init__(self, description, name, value):
        self.description = description
        self.name = name
        self.value = value
        self.__class__._registry.append(self)
