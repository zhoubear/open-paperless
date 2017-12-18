from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

from .literals import (
    DEFAULT_LIBREOFFICE_PATH, DEFAULT_PDFTOPPM_DPI, DEFAULT_PDFTOPPM_FORMAT,
    DEFAULT_PDFTOPPM_PATH, DEFAULT_PDFINFO_PATH, DEFAULT_PILLOW_FORMAT
)

namespace = Namespace(name='converter', label=_('Converter'))
setting_graphics_backend = namespace.add_setting(
    default='converter.backends.python.Python',
    help_text=_('Graphics conversion backend to use.'),
    global_name='CONVERTER_GRAPHICS_BACKEND',
)
setting_graphics_backend_config = namespace.add_setting(
    default='''
        {{
            libreoffice_path: {},
            pdftoppm_dpi: {},
            pdftoppm_format: {},
            pdftoppm_path: {},
            pdfinfo_path: {},
            pillow_format: {}

        }}
    '''.replace('\n', '').format(
        DEFAULT_LIBREOFFICE_PATH, DEFAULT_PDFTOPPM_DPI,
        DEFAULT_PDFTOPPM_FORMAT, DEFAULT_PDFTOPPM_PATH, DEFAULT_PDFINFO_PATH,
        DEFAULT_PILLOW_FORMAT
    ), help_text=_(
        'Configuration options for the graphics conversion backend.'
    ), global_name='CONVERTER_GRAPHICS_BACKEND_CONFIG',
)
