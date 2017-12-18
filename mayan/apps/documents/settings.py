from __future__ import unicode_literals

import pycountry

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

LANGUAGE_CHOICES = [
    (i.iso639_3_code, i.name) for i in list(pycountry.languages)
]

namespace = Namespace(name='documents', label=_('Documents'))
setting_display_size = namespace.add_setting(
    global_name='DOCUMENTS_DISPLAY_SIZE', default='3600'
)
setting_preview_size = namespace.add_setting(
    global_name='DOCUMENTS_PREVIEW_SIZE', default='800'
)
setting_print_size = namespace.add_setting(
    global_name='DOCUMENTS_PRINT_SIZE', default='3600'
)
setting_thumbnail_size = namespace.add_setting(
    global_name='DOCUMENTS_THUMBNAIL_SIZE', default='800'
)
setting_recent_count = namespace.add_setting(
    global_name='DOCUMENTS_RECENT_COUNT', default=40,
    help_text=_(
        'Maximum number of recent (created, edited, viewed) documents to '
        'remember per user.'
    )
)
setting_storage_backend = namespace.add_setting(
    global_name='DOCUMENTS_STORAGE_BACKEND',
    default='storage.backends.filebasedstorage.FileBasedStorage'
)
setting_zoom_percent_step = namespace.add_setting(
    global_name='DOCUMENTS_ZOOM_PERCENT_STEP', default=25,
    help_text=_(
        'Amount in percent zoom in or out a document page per user '
        'interaction.'
    )
)
setting_zoom_max_level = namespace.add_setting(
    global_name='DOCUMENTS_ZOOM_MAX_LEVEL', default=300,
    help_text=_(
        'Maximum amount in percent (%) to allow user to zoom in a document '
        'page interactively.'
    )
)
setting_zoom_min_level = namespace.add_setting(
    global_name='DOCUMENTS_ZOOM_MIN_LEVEL', default=25,
    help_text=_(
        'Minimum amount in percent (%) to allow user to zoom out a document '
        'page interactively.'
    )
)
setting_rotation_step = namespace.add_setting(
    global_name='DOCUMENTS_ROTATION_STEP', default=90,
    help_text=_(
        'Amount in degrees to rotate a document page per user interaction.'
    )
)
setting_cache_storage_backend = namespace.add_setting(
    global_name='DOCUMENTS_CACHE_STORAGE_BACKEND',
    default='documents.storage.LocalCacheFileStorage'
)
setting_language = namespace.add_setting(
    global_name='DOCUMENTS_LANGUAGE', default='eng',
    help_text=_('Default documents language (in ISO639-2 format).')
)
setting_language_choices = namespace.add_setting(
    global_name='DOCUMENTS_LANGUAGE_CHOICES', default=LANGUAGE_CHOICES,
    help_text=_('List of supported document languages.')
)
setting_disable_base_image_cache = namespace.add_setting(
    global_name='DOCUMENTS_DISABLE_BASE_IMAGE_CACHE', default=False,
    help_text=_(
        'Disables the first cache tier which stores high resolution, '
        'non transformed versions of documents\'s pages.'
    )
)
setting_disable_transformed_image_cache = namespace.add_setting(
    global_name='DOCUMENTS_DISABLE_TRANSFORMED_IMAGE_CACHE', default=False,
    help_text=_(
        'Disables the second cache tier which stores medium to low '
        'resolution, transformed (rotated, zoomed, etc) versions '
        'of documents\' pages.'
    )
)
