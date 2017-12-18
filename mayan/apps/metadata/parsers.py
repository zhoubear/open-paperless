from __future__ import unicode_literals

from dateutil.parser import parse

from django.core.exceptions import ValidationError


class MetadataParser(object):
    _registry = []

    @classmethod
    def register(cls, parser):
        cls._registry.append(parser)

    @classmethod
    def get_all(cls):
        return cls._registry

    @classmethod
    def get_import_path(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_import_paths(cls):
        return [validator.get_import_path() for validator in cls.get_all()]

    def execute(self, input_data):
        raise NotImplementedError

    def parse(self, input_data):
        try:
            return self.execute(input_data)
        except Exception as exception:
            raise ValidationError(exception)


class DateAndTimeParser(MetadataParser):
    def execute(self, input_data):
        return parse(input_data).isoformat()


class DateParser(MetadataParser):
    def execute(self, input_data):
        return parse(input_data).date().isoformat()


class TimeParser(MetadataParser):
    def execute(self, input_data):
        return parse(input_data).time().isoformat()


MetadataParser.register(DateAndTimeParser)
MetadataParser.register(DateParser)
MetadataParser.register(TimeParser)
