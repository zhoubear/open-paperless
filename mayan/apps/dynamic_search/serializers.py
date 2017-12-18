from __future__ import unicode_literals

from rest_framework import serializers


class SearchFieldSerializer(serializers.Serializer):
    field = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)


class SearchModelSerializer(serializers.Serializer):
    app_label = serializers.CharField(read_only=True)
    model_name = serializers.CharField(read_only=True)
    pk = serializers.CharField(read_only=True)
    search_fields = SearchFieldSerializer(many=True, read_only=True)
