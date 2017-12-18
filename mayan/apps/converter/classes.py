from __future__ import unicode_literals

import base64
from io import BytesIO
import logging
import os

from PIL import Image, ImageFilter
import sh
import yaml

from django.utils.six import text_type
from django.utils.translation import string_concat, ugettext_lazy as _

from common.settings import setting_temporary_directory
from common.utils import fs_cleanup, mkdtemp, mkstemp
from mimetype.api import get_mimetype

from .exceptions import InvalidOfficeFormat, OfficeConversionError
from .literals import (
    DEFAULT_LIBREOFFICE_PATH, DEFAULT_PAGE_NUMBER, DEFAULT_PILLOW_FORMAT
)
from .settings import setting_graphics_backend_config

CHUNK_SIZE = 1024
logger = logging.getLogger(__name__)

try:
    LIBREOFFICE = sh.Command(
        yaml.load(setting_graphics_backend_config.value).get(
            'libreoffice_path', DEFAULT_LIBREOFFICE_PATH
        )
    ).bake('--headless', '--convert-to', 'pdf:writer_pdf_Export')
except sh.CommandNotFound:
    LIBREOFFICE = None


CONVERTER_OFFICE_FILE_MIMETYPES = (
    'application/msword',
    'application/mswrite',
    'application/mspowerpoint',
    'application/msexcel',
    'application/pgp-keys',
    'application/vnd.ms-excel',
    'application/vnd.ms-excel.addin.macroEnabled.12',
    'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
    'application/vnd.ms-powerpoint',
    'application/vnd.oasis.opendocument.chart',
    'application/vnd.oasis.opendocument.chart-template',
    'application/vnd.oasis.opendocument.formula',
    'application/vnd.oasis.opendocument.formula-template',
    'application/vnd.oasis.opendocument.graphics',
    'application/vnd.oasis.opendocument.graphics-template',
    'application/vnd.oasis.opendocument.image',
    'application/vnd.oasis.opendocument.image-template',
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.oasis.opendocument.presentation-template',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    'application/vnd.openxmlformats-officedocument.presentationml.template',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.slide',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.spreadsheet-template',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.oasis.opendocument.text-master',
    'application/vnd.oasis.opendocument.text-template',
    'application/vnd.oasis.opendocument.text-web',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-office',
    'application/xml',
    'text/x-c',
    'text/x-c++',
    'text/x-pascal',
    'text/x-msdos-batch',
    'text/x-python',
    'text/x-shellscript',
    'text/plain',
    'text/rtf',
)


class ConverterBase(object):
    def __init__(self, file_object, mime_type=None):
        self.file_object = file_object
        self.image = None
        self.mime_type = mime_type or get_mimetype(
            file_object=file_object, mimetype_only=False
        )[0]
        self.soffice_file = None

    def to_pdf(self):
        if self.mime_type in CONVERTER_OFFICE_FILE_MIMETYPES:
            return self.soffice()
        else:
            raise InvalidOfficeFormat(_('Not an office file format.'))

    def seek(self, page_number):
        # Starting with #0
        self.file_object.seek(0)

        try:
            self.image = Image.open(self.file_object)
        except IOError:
            # Cannot identify image file
            self.image = self.convert(page_number=page_number)
        else:
            self.image.seek(page_number)
            self.image.load()

    def soffice(self):
        """
        Executes LibreOffice as a subprocess
        """
        if not LIBREOFFICE:
            raise OfficeConversionError(
                _('LibreOffice not installed or not found.')
            )

        new_file_object, input_filepath = mkstemp()
        self.file_object.seek(0)
        os.write(new_file_object, self.file_object.read())
        self.file_object.seek(0)
        os.lseek(new_file_object, 0, os.SEEK_SET)
        os.close(new_file_object)

        libreoffice_filter = None
        if self.mime_type == 'text/plain':
            libreoffice_filter = 'Text (encoded):UTF8,LF,,,'

        libreoffice_home_directory = mkdtemp()
        args = (
            input_filepath, '--outdir', setting_temporary_directory.value,
            '-env:UserInstallation=file://{}'.format(
                os.path.join(
                    libreoffice_home_directory, 'LibreOffice_Conversion'
                )
            ),
        )

        kwargs = {'_env': {'HOME': libreoffice_home_directory}}

        if libreoffice_filter:
            kwargs.update({'infilter': libreoffice_filter})

        try:
            LIBREOFFICE(*args, **kwargs)
        except sh.ErrorReturnCode as exception:
            raise OfficeConversionError(exception)
        except Exception as exception:
            logger.error('Exception launching Libre Office; %s', exception)
            raise
        finally:
            fs_cleanup(input_filepath)
            fs_cleanup(libreoffice_home_directory)

        filename, extension = os.path.splitext(
            os.path.basename(input_filepath)
        )
        logger.debug('filename: %s', filename)
        logger.debug('extension: %s', extension)

        converted_output = os.path.join(
            setting_temporary_directory.value, os.path.extsep.join(
                (filename, 'pdf')
            )
        )
        logger.debug('converted_output: %s', converted_output)

        with open(converted_output) as converted_file_object:
            while True:
                data = converted_file_object.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

        fs_cleanup(input_filepath)
        fs_cleanup(converted_output)

    def get_page(self, output_format=None, as_base64=False):
        output_format = output_format or yaml.load(
            setting_graphics_backend_config.value
        ).get(
            'pillow_format', DEFAULT_PILLOW_FORMAT
        )

        if not self.image:
            self.seek(0)

        image_buffer = BytesIO()
        new_mode = self.image.mode

        if output_format.upper() == 'JPEG':
            # JPEG doesn't support transparency channel, convert the image to
            # RGB. Removes modes: P and RGBA
            new_mode = 'RGB'

        self.image.convert(new_mode).save(image_buffer, format=output_format)

        if as_base64:
            return 'data:{};base64,{}'.format(Image.MIME[output_format], base64.b64encode(image_buffer.getvalue()))
        else:
            image_buffer.seek(0)

        return image_buffer

    def convert(self, page_number=DEFAULT_PAGE_NUMBER):
        self.page_number = page_number

    def transform(self, transformation):
        if not self.image:
            self.seek(0)

        self.image = transformation.execute_on(self.image)

    def transform_many(self, transformations):
        if not self.image:
            self.seek(0)

        for transformation in transformations:
            self.image = transformation.execute_on(self.image)

    def get_page_count(self):
        try:
            self.soffice_file = self.to_pdf()
        except InvalidOfficeFormat as exception:
            logger.debug('Is not an office format document; %s', exception)

    def detect_orientation(self, page_number):
        # Must be overrided by subclass
        pass


class BaseTransformation(object):
    """
    Transformation can modify the appearance of the document's page preview.
    Some transformation available are: Rotate, zoom, resize and crop.
    """
    arguments = ()
    name = 'base_transformation'
    _registry = {}

    @staticmethod
    def encode_hash(decoded_value):
        return hex(abs(decoded_value))[2:]

    @staticmethod
    def decode_hash(encoded_value):
        return int(encoded_value, 16)

    @staticmethod
    def combine(transformations):
        result = None

        for index, transformation in enumerate(transformations):
            if not result:
                result = hash((BaseTransformation.decode_hash(transformation.cache_hash()), index))
            else:
                result ^= hash((BaseTransformation.decode_hash(transformation.cache_hash()), index))

        return BaseTransformation.encode_hash(result)

    @classmethod
    def register(cls, transformation):
        cls._registry[transformation.name] = transformation

    @classmethod
    def get_transformation_choices(cls):
        return sorted(
            [
                (name, klass.get_label()) for name, klass in cls._registry.items()
            ]
        )

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_label(cls):
        if cls.arguments:
            return string_concat(cls.label, ': ', ', '.join(cls.arguments))
        else:
            return cls.label

    def __init__(self, **kwargs):
        self.kwargs = {}
        for argument_name in self.arguments:
            setattr(self, argument_name, kwargs.get(argument_name))
            self.kwargs[argument_name] = kwargs.get(argument_name)

    def cache_hash(self):
        result = text_type.__hash__(self.name)
        for index, (key, value) in enumerate(self.kwargs.items()):
            result ^= hash((key, index)) ^ hash((value, index))

        return BaseTransformation.encode_hash(result)

    def execute_on(self, image):
        self.image = image
        self.aspect = 1.0 * image.size[0] / image.size[1]


class TransformationCrop(BaseTransformation):
    arguments = ('left', 'top', 'right', 'bottom',)
    label = _('Crop')
    name = 'crop'

    def execute_on(self, *args, **kwargs):
        super(TransformationCrop, self).execute_on(*args, **kwargs)

        return self.image.crop(
            (self.left, self.top, self.right, self.bottom)
        )


class TransformationFlip(BaseTransformation):
    arguments = ()
    label = _('Flip')
    name = 'flip'

    def execute_on(self, *args, **kwargs):
        super(TransformationFlip, self).execute_on(*args, **kwargs)

        return self.image.transpose(Image.FLIP_TOP_BOTTOM)


class TransformationGaussianBlur(BaseTransformation):
    arguments = ('radius',)
    label = _('Gaussian blur')
    name = 'gaussianblur'

    def execute_on(self, *args, **kwargs):
        super(TransformationGaussianBlur, self).execute_on(*args, **kwargs)

        return self.image.filter(ImageFilter.GaussianBlur(radius=self.radius))


class TransformationLineArt(BaseTransformation):
    label = _('Line art')
    name = 'lineart'

    def execute_on(self, *args, **kwargs):
        super(TransformationLineArt, self).execute_on(*args, **kwargs)

        return self.image.convert('L').point(lambda x: 0 if x < 128 else 255, '1')


class TransformationMirror(BaseTransformation):
    arguments = ()
    label = _('Mirror')
    name = 'mirror'

    def execute_on(self, *args, **kwargs):
        super(TransformationMirror, self).execute_on(*args, **kwargs)

        return self.image.transpose(Image.FLIP_LEFT_RIGHT)


class TransformationResize(BaseTransformation):
    arguments = ('width', 'height')
    label = _('Resize')
    name = 'resize'

    def execute_on(self, *args, **kwargs):
        super(TransformationResize, self).execute_on(*args, **kwargs)

        width = int(self.width)
        height = int(self.height or 1.0 * width / self.aspect)

        factor = 1
        while self.image.size[0] / factor > 2 * width and self.image.size[1] * 2 / factor > 2 * height:
            factor *= 2

        if factor > 1:
            self.image.thumbnail(
                (self.image.size[0] / factor, self.image.size[1] / factor),
                Image.NEAREST
            )

        # Resize the image with best quality algorithm ANTI-ALIAS
        self.image.thumbnail((width, height), Image.ANTIALIAS)

        return self.image


class TransformationRotate(BaseTransformation):
    arguments = ('degrees',)
    label = _('Rotate')
    name = 'rotate'

    def execute_on(self, *args, **kwargs):
        super(TransformationRotate, self).execute_on(*args, **kwargs)

        self.degrees %= 360

        if self.degrees == 0:
            return self.image

        return self.image.rotate(
            360 - self.degrees, resample=Image.BICUBIC, expand=True
        )


class TransformationRotate90(TransformationRotate):
    arguments = ()
    degrees = 90
    label = _('Rotate 90 degrees')
    name = 'rotate90'

    def __init__(self, **kwargs):
        super(TransformationRotate90, self).__init__()
        self.kwargs['degrees'] = 90


class TransformationRotate180(TransformationRotate):
    arguments = ()
    degrees = 180
    label = _('Rotate 180 degrees')
    name = 'rotate180'

    def __init__(self, **kwargs):
        super(TransformationRotate180, self).__init__()
        self.kwargs['degrees'] = 180


class TransformationRotate270(TransformationRotate):
    arguments = ()
    degrees = 270
    label = _('Rotate 270 degrees')
    name = 'rotate270'

    def __init__(self, **kwargs):
        super(TransformationRotate270, self).__init__()
        self.kwargs['degrees'] = 270


class TransformationUnsharpMask(BaseTransformation):
    arguments = ('radius', 'percent', 'threshold')
    label = _('Unsharp masking')
    name = 'unsharpmask'

    def execute_on(self, *args, **kwargs):
        super(TransformationUnsharpMask, self).execute_on(*args, **kwargs)

        return self.image.filter(
            ImageFilter.UnsharpMask(
                radius=self.radius, percent=self.percent,
                threshold=self.threshold
            )
        )


class TransformationZoom(BaseTransformation):
    arguments = ('percent',)
    label = _('Zoom')
    name = 'zoom'

    def execute_on(self, *args, **kwargs):
        super(TransformationZoom, self).execute_on(*args, **kwargs)

        if self.percent == 100:
            return self.image

        decimal_value = float(self.percent) / 100
        return self.image.resize(
            (
                int(self.image.size[0] * decimal_value),
                int(self.image.size[1] * decimal_value)
            ), Image.ANTIALIAS
        )


BaseTransformation.register(TransformationCrop)
BaseTransformation.register(TransformationFlip)
BaseTransformation.register(TransformationGaussianBlur)
BaseTransformation.register(TransformationLineArt)
BaseTransformation.register(TransformationMirror)
BaseTransformation.register(TransformationResize)
BaseTransformation.register(TransformationRotate)
BaseTransformation.register(TransformationRotate90)
BaseTransformation.register(TransformationRotate180)
BaseTransformation.register(TransformationRotate270)
BaseTransformation.register(TransformationUnsharpMask)
BaseTransformation.register(TransformationZoom)
