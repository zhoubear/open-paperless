from __future__ import unicode_literals

import datetime
from errno import ENOENT
import logging
from stat import S_IFDIR, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations

from django.core import management
from django.core.cache import caches
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import CommandError
from django.db.models import Count

from document_indexing.models import Index, IndexInstanceNode
from documents.models import Document

from ...literals import (
    MAX_FILE_DESCRIPTOR, MIN_FILE_DESCRIPTOR, FILE_MODE, DIRECTORY_MODE
)
from ...settings import (
    setting_document_lookup_cache_timeout, setting_node_lookup_cache_timeout
)

logger = logging.getLogger(__name__)


class IndexFS(Operations):
    def _get_next_file_descriptor(self):
        while(True):
            self.file_descriptor_count += 1
            if self.file_descriptor_count > MAX_FILE_DESCRIPTOR:
                self.file_descriptor_count = MIN_FILE_DESCRIPTOR

            try:
                if not self.file_descriptors[self.file_descriptor_count]:
                    return self.file_descriptor_count
            except KeyError:
                return self.file_descriptor_count

    def _path_to_node(self, path, access_only=False, directory_only=True):
        logger.debug('path: %s', path)
        logger.debug('directory_only: %s', directory_only)

        parts = path.split('/')

        logger.debug('parts: %s', parts)

        node = self.index.instance_root

        if len(parts) > 1 and parts[1] != '':
            obj = self.cache.get(path)

            if obj:
                node_pk = obj.get('node_pk')
                if node_pk:
                    if access_only:
                        return True
                    else:
                        return IndexInstanceNode.objects.get(pk=node_pk)

                document_pk = obj.get('document_pk')
                if document_pk:
                    if access_only:
                        return True
                    else:
                        return Document.objects.get(pk=document_pk)

            for count, part in enumerate(parts[1:]):
                try:
                    node = node.children.get(value=part)
                except IndexInstanceNode.DoesNotExist:
                    logger.debug('%s does not exists', part)

                    if directory_only:
                        return None
                    else:
                        try:
                            if node.index_template_node.link_documents:
                                result = node.documents.get(label=part)
                                logger.debug(
                                    'path %s is a valid file path', path
                                )
                                self.cache.set(
                                    path, {'document_pk': result.pk},
                                    setting_document_lookup_cache_timeout.value
                                )

                                return result
                            else:
                                return None
                        except Document.DoesNotExist:
                            logger.debug(
                                'path %s is a file, but is not found', path
                            )
                            return None
                        except MultipleObjectsReturned:
                            return None
                except MultipleObjectsReturned:
                    return None

            self.cache.set(
                path, {'node_pk': node.pk},
                setting_node_lookup_cache_timeout.value
            )

        logger.debug('node: %s', node)
        logger.debug('node is root: %s', node.is_root_node())

        return node

    def __init__(self, index_slug):
        self.file_descriptor_count = MIN_FILE_DESCRIPTOR
        self.file_descriptors = {}
        self.cache = caches['default']

        try:
            self.index = Index.objects.get(slug=index_slug)
        except Index.DoesNotExist:
            print 'Unknown index slug: {}.'.format(index_slug)
            exit(1)

    def access(self, path, fh=None):
        result = self._path_to_node(
            path=path, access_only=True, directory_only=False
        )

        if not result:
            raise FuseOSError(ENOENT)

    def getattr(self, path, fh=None):
        logger.debug('path: %s, fh: %s', path, fh)

        now = time()
        result = self._path_to_node(path=path, directory_only=False)

        if not result:
            raise FuseOSError(ENOENT)

        if isinstance(result, IndexInstanceNode):
            return {
                'st_mode': (S_IFDIR | DIRECTORY_MODE), 'st_ctime': now,
                'st_mtime': now, 'st_atime': now, 'st_nlink': 2
            }
        else:
            return {
                'st_mode': (S_IFREG | FILE_MODE),
                'st_ctime': (
                    result.date_added.replace(tzinfo=None) - result.date_added.utcoffset() - datetime.datetime(1970, 1, 1)
                ).total_seconds(),
                'st_mtime': (
                    result.latest_version.timestamp.replace(tzinfo=None) - result.latest_version.timestamp.utcoffset() - datetime.datetime(1970, 1, 1)
                ).total_seconds(),
                'st_atime': now,
                'st_size': result.size
            }

    def open(self, path, flags):
        result = self._path_to_node(path=path, directory_only=False)

        if isinstance(result, Document):
            next_file_descriptor = self._get_next_file_descriptor()
            self.file_descriptors[next_file_descriptor] = result.open()
            return next_file_descriptor
        else:
            raise FuseOSError(ENOENT)

    def release(self, path, fh):
        self.file_descriptors[fh] = None
        del(self.file_descriptors[fh])

    def read(self, path, size, offset, fh):
        self.file_descriptors[fh].seek(offset)
        return self.file_descriptors[fh].read(size)

    def readdir(self, path, fh):
        logger.debug('path: %s', path)

        node = self._path_to_node(path=path, directory_only=True)

        if not node:
            raise FuseOSError(ENOENT)

        yield '.'
        yield '..'

        # Nodes
        queryset = node.get_children().values('value').exclude(
            value__contains='/'
        )

        for duplicate in queryset.order_by().annotate(count_id=Count('id')).filter(count_id__gt=1):
            queryset = queryset.exclude(label=duplicate['label'])

        for child_node in queryset.values_list('value', flat=True):
            yield child_node

        # Documents
        if node.index_template_node.link_documents:
            queryset = node.documents.values('label').exclude(
                label__contains='/'
            )

            for duplicate in queryset.order_by().annotate(count_id=Count('id')).filter(count_id__gt=1):
                queryset = queryset.exclude(label=duplicate['label'])

            for document_label in queryset.values_list('label', flat=True):
                yield document_label


class Command(management.BaseCommand):
    help = 'Mount an index as a FUSE filesystem.'

    def add_arguments(self, parser):
        parser.add_argument('slug', nargs='?', help='Index slug')
        parser.add_argument('mount_point', nargs='?', help='Mount point')
        parser.add_argument(
            '--allow-other', action='store_true', dest='allow_other',
            default=False,
            help='All users (including root) can access the index files.'
        )
        parser.add_argument(
            '--allow-root', action='store_true', dest='allow_root',
            default=False,
            help='Mount access is limited to the user mounting the index and '
            'root. This option and --allow-other are mutually exclusive.'
        )

    def handle(self, *args, **options):
        if not options.get('slug') or not options.get('mount_point'):
            self.stderr.write(self.style.ERROR('Incorrect number of arguments'))
            exit(1)

        try:
            FUSE(
                operations=IndexFS(index_slug=options['slug']),
                mountpoint=options['mount_point'], nothreads=True, foreground=True,
                allow_other=options['allow_other'],
                allow_root=options['allow_root']
            )
        except RuntimeError:
            if options['allow_other'] or options['allow_root']:
                raise CommandError(
                    'Make sure \'user_allow_other\' is set in /etc/fuse.conf'
                )
            else:
                raise
