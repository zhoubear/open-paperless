from __future__ import unicode_literals

import logging

from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import StagingFolderSource, WebFormSource

logger = logging.getLogger(__name__)


class StagingFolderFileSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('get_url')
    image_url = serializers.SerializerMethodField('get_image_url')
    filename = serializers.CharField(max_length=255)

    def get_url(self, obj):
        return reverse(
            'stagingfolderfile-detail',
            args=(obj.staging_folder.pk, obj.encoded_filename,),
            request=self.context.get('request')
        )

    def get_image_url(self, obj):
        return reverse(
            'stagingfolderfile-image-view',
            args=(obj.staging_folder.pk, obj.encoded_filename,),
            request=self.context.get('request')
        )


class StagingFolderSerializer(serializers.HyperlinkedModelSerializer):
    files = serializers.SerializerMethodField('get_files')

    def get_files(self, obj):
        try:
            return [
                StagingFolderFileSerializer(entry, context=self.context).data for entry in obj.get_files()
            ]
        except Exception as exception:
            logger.error('unhandled exception: %s', exception)
            return []

    class Meta:
        model = StagingFolderSource


class WebFormSourceSerializer(serializers.Serializer):
    class Meta:
        model = WebFormSource


class NewDocumentSerializer(serializers.Serializer):
    source = serializers.IntegerField()
    document_type = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False)
    expand = serializers.BooleanField(default=False)
    file = serializers.FileField()
    filename = serializers.CharField(required=False)
    use_file_name = serializers.BooleanField(default=False)
