from __future__ import absolute_import, unicode_literals

import logging

from PIL import Image
import pyocr
import pyocr.builders

from ..classes import OCRBackendBase
from ..exceptions import OCRError

logger = logging.getLogger(__name__)


class PyOCR(OCRBackendBase):
    def __init__(self, *args, **kwargs):
        super(PyOCR, self).__init__(*args, **kwargs)

        self.languages = ()

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise OCRError('No OCR tool found')

        self.tool = tools[0]

        # The tools are returned in the recommended order of usage
        for tool in tools:
            if tool.__name__ == 'pyocr.libtesseract':
                self.tool = tool

        logger.debug('Will use tool \'%s\'', self.tool.get_name())

        self.languages = self.tool.get_available_languages()
        logger.debug('Available languages: %s', ', '.join(self.languages))

    def execute(self, *args, **kwargs):
        """
        Execute the command line binary of tesseract
        """
        super(PyOCR, self).execute(*args, **kwargs)

        image = Image.open(self.converter.get_page())
        try:
            result = self.tool.image_to_string(
                image,
                lang=self.language,
                builder=pyocr.builders.TextBuilder()
            )
        except Exception as exception:
            error_message = 'Exception calling pyocr with language option: '
            '{}; {}'.format(self.language, exception)

            if self.language not in self.languages:
                error_message = '{}\nThe requested OCR language "{}" is not '
                'available and needs to be installed.\n'.format(
                    error_message, self.language
                )

            logger.error(error_message)
            raise OCRError(error_message)
        else:
            return result
