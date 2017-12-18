from __future__ import unicode_literals

from documents.settings import setting_preview_size, setting_thumbnail_size
from documents.widgets import BaseDocumentThumbnailWidget


class StagingFileThumbnailWidget(BaseDocumentThumbnailWidget):
    disable_title_link = True
    gallery_name = 'sources:staging_list'
    click_view_name = 'rest_api:stagingfolderfile-image-view'
    click_view_query_dict = {
        'size': setting_preview_size.value
    }
    preview_view_name = 'rest_api:stagingfolderfile-image-view'
    preview_view_query_dict = {
        'size': setting_thumbnail_size.value
    }

    def get_click_view_kwargs(self, instance):
        return {
            'staging_folder_pk': instance.staging_folder.pk,
            'encoded_filename': instance.encoded_filename
        }

    def get_preview_view_kwargs(self, instance):
        return {
            'staging_folder_pk': instance.staging_folder.pk,
            'encoded_filename': instance.encoded_filename
        }

    def get_title(self, instance):
        return instance.filename
