from __future__ import unicode_literals

from django.utils.module_loading import import_string
from django.utils.six import string_types
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class DynamicSerializerField(serializers.ReadOnlyField):
    serializers = {}

    @classmethod
    def add_serializer(cls, klass, serializer_class):
        if isinstance(klass, string_types):
            klass = import_string(klass)

        if isinstance(serializer_class, string_types):
            serializer_class = import_string(serializer_class)

        cls.serializers[klass] = serializer_class

    def to_representation(self, value):
        for klass, serializer_class in self.serializers.items():
            if isinstance(value, klass):
                return serializer_class(
                    context={'request': self.context['request']}
                ).to_representation(instance=value)

        return _('Unable to find serializer class for: %s') % value
