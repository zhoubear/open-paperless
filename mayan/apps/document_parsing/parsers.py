from __future__ import unicode_literals

import logging
import os
import subprocess

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from common.utils import copyfile, fs_cleanup, mkstemp

from .exceptions import ParserError
from .settings import setting_pdftotext_path

logger = logging.getLogger(__name__)


class Parser(object):
    """
    Parser base class
    """

    _registry = {}

    @classmethod
    def register(cls, mimetypes, parser_classes):
        for mimetype in mimetypes:
            for parser_class in parser_classes:
                cls._registry.setdefault(
                    mimetype, []
                ).append(parser_class)

    @classmethod
    def parse_document_version(cls, document_version):
        for parser_class in cls._registry.get(document_version.mimetype, ()):
            try:
                parser = parser_class()
                parser.process_document_version(document_version)
            except ParserError:
                # If parser raises error, try next parser in the list
                pass
            else:
                # If parser was successfull there is no need to try
                # others in the list for this mimetype
                return

    @classmethod
    def parse_document_page(cls, document_page):
        for parser_class in cls._registry.get(document_page.document_version.mimetype, ()):
            try:
                parser = parser_class()
                parser.process_document_page(document_page)
            except ParserError:
                # If parser raises error, try next parser in the list
                pass
            else:
                # If parser was successfull there is no need to try
                # others in the list for this mimetype
                return

    def process_document_version(self, document_version):
        logger.info(
            'Starting parsing for document version: %s', document_version
        )
        logger.debug('document version: %d', document_version.pk)

        for document_page in document_version.pages.all():
            self.process_document_page(document_page=document_page)

    def process_document_page(self, document_page):
        DocumentPageContent = apps.get_model(
            app_label='document_parsing', model_name='DocumentPageContent'
        )

        logger.info(
            'Processing page: %d of document version: %s',
            document_page.page_number, document_page.document_version
        )

        file_object = document_page.document_version.get_intermidiate_file()

        try:
            document_page_content, created = DocumentPageContent.objects.get_or_create(
                document_page=document_page
            )
            document_page_content.content = self.execute(
                file_object=file_object, page_number=document_page.page_number
            )
            document_page_content.save()
        except Exception as exception:
            error_message = _('Exception parsing page; %s') % exception
            logger.error(error_message)
            raise ParserError(error_message)
        finally:
            file_object.close()

        logger.info(
            'Finished processing page: %d of document version: %s',
            document_page.page_number, document_page.document_version
        )

    def execute(self, file_object, page_number):
        raise NotImplementedError(
            'Your %s class has not defined the required execute() method.' %
            self.__class__.__name__
        )


class PopplerParser(Parser):
    """
    PDF parser using the pdftotext execute from the poppler package
    """

    def __init__(self):
        self.pdftotext_path = setting_pdftotext_path.value
        if not os.path.exists(self.pdftotext_path):
            error_message = _(
                'Cannot find pdftotext executable at: %s'
            ) % self.pdftotext_path
            logger.error(error_message)
            raise ParserError(error_message)

        logger.debug('self.pdftotext_path: %s', self.pdftotext_path)

    def execute(self, file_object, page_number):
        logger.debug('Parsing PDF page: %d', page_number)

        destination_descriptor, temp_filepath = mkstemp()
        copyfile(file_object, temp_filepath)

        command = []
        command.append(self.pdftotext_path)
        command.append('-f')
        command.append(str(page_number))
        command.append('-l')
        command.append(str(page_number))
        command.append(temp_filepath)
        command.append('-')

        proc = subprocess.Popen(
            command, close_fds=True, stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return_code = proc.wait()
        if return_code != 0:
            logger.error(proc.stderr.readline())
            fs_cleanup(temp_filepath, file_descriptor=destination_descriptor)

            raise ParserError

        output = proc.stdout.read()
        fs_cleanup(temp_filepath, file_descriptor=destination_descriptor)

        if output == b'\x0c':
            logger.debug('Parser didn\'t return any output')
            return ''

        if output[-3:] == b'\x0a\x0a\x0c':
            return output[:-3]

        return output


Parser.register(
    mimetypes=('application/pdf',),
    parser_classes=(PopplerParser,)
)
