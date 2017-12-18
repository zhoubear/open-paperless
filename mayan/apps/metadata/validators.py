from __future__ import unicode_literals

from dateutil.parser import parse

from django.core.exceptions import ValidationError

from .parsers import MetadataParser


class MetadataValidator(MetadataParser):
    _registry = []

    def validate(self, input_data):
        try:
            self.execute(input_data)
        except Exception as exception:
            raise ValidationError(exception)


class DateAndTimeValidator(MetadataValidator):
    def execute(self, input_data):
        return parse(input_data).isoformat()


class DateValidator(MetadataValidator):
    def execute(self, input_data):
        return parse(input_data).date().isoformat()


class TimeValidator(MetadataValidator):
    def execute(self, input_data):
        return parse(input_data).time().isoformat()


MetadataValidator.register(DateAndTimeValidator)
MetadataValidator.register(DateValidator)
MetadataValidator.register(TimeValidator)
