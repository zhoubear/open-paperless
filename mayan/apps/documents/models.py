from __future__ import absolute_import, unicode_literals

import hashlib
import logging
import os
import uuid

from django.conf import settings
from django.core.files import File
from django.db import models, transaction
from django.template import Template, Context
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from acls.models import AccessControlList
from common.literals import TIME_DELTA_UNIT_CHOICES
from converter import (
    converter_class, BaseTransformation, TransformationResize,
    TransformationRotate, TransformationZoom
)
from converter.exceptions import InvalidOfficeFormat, PageCountError
from converter.literals import DEFAULT_ZOOM_LEVEL, DEFAULT_ROTATION
from converter.models import Transformation
from mimetype.api import get_mimetype

from .events import (
    event_document_create, event_document_new_version,
    event_document_properties_edit, event_document_type_change,
    event_document_version_revert
)
from .literals import DEFAULT_DELETE_PERIOD, DEFAULT_DELETE_TIME_UNIT
from .managers import (
    DocumentManager, DocumentTypeManager, DuplicatedDocumentManager,
    PassthroughManager, RecentDocumentManager, TrashCanManager
)
from .permissions import permission_document_view
from .runtime import cache_storage_backend, storage_backend
from .settings import (
    setting_disable_base_image_cache, setting_disable_transformed_image_cache,
    setting_display_size, setting_language, setting_zoom_max_level,
    setting_zoom_min_level
)
from .signals import (
    post_document_created, post_document_type_change, post_version_upload
)

logger = logging.getLogger(__name__)


# document image cache name hash function
def HASH_FUNCTION(data):
    return hashlib.sha256(data).hexdigest()


def UUID_FUNCTION(*args, **kwargs):
    return force_text(uuid.uuid4())


@python_2_unicode_compatible
class DocumentType(models.Model):
    """
    Define document types or classes to which a specific set of
    properties can be attached
    """
    label = models.CharField(
        max_length=32, unique=True, verbose_name=_('Label')
    )
    trash_time_period = models.PositiveIntegerField(
        blank=True, help_text=_(
            'Amount of time after which documents of this type will be '
            'moved to the trash.'
        ), null=True, verbose_name=_('Trash time period')
    )
    trash_time_unit = models.CharField(
        blank=True, choices=TIME_DELTA_UNIT_CHOICES, null=True, max_length=8,
        verbose_name=_('Trash time unit')
    )
    delete_time_period = models.PositiveIntegerField(
        blank=True, default=DEFAULT_DELETE_PERIOD, help_text=_(
            'Amount of time after which documents of this type in the trash '
            'will be deleted.'
        ), null=True, verbose_name=_('Delete time period')
    )
    delete_time_unit = models.CharField(
        blank=True, choices=TIME_DELTA_UNIT_CHOICES,
        default=DEFAULT_DELETE_TIME_UNIT, max_length=8, null=True,
        verbose_name=_('Delete time unit')
    )

    objects = DocumentTypeManager()

    def __str__(self):
        return self.label

    def delete(self, *args, **kwargs):
        for document in Document.passthrough.filter(document_type=self):
            document.delete(to_trash=False)

        return super(DocumentType, self).delete(*args, **kwargs)

    def natural_key(self):
        return (self.label,)

    class Meta:
        ordering = ('label',)
        verbose_name = _('Document type')
        verbose_name_plural = _('Documents types')

    @property
    def deleted_documents(self):
        return DeletedDocument.objects.filter(document_type=self)

    def get_document_count(self, user):
        queryset = AccessControlList.objects.filter_by_access(
            permission_document_view, user, queryset=self.documents
        )

        return queryset.count()

    def new_document(self, file_object, label=None, description=None, language=None, _user=None):
        try:
            with transaction.atomic():
                document = self.documents.create(
                    description=description or '',
                    label=label or file_object.name,
                    language=language or setting_language.value
                )
                document.save(_user=_user)

                document.new_version(file_object=file_object, _user=_user)
                return document
        except Exception as exception:
            logger.critical(
                'Unexpected exception while trying to create new document '
                '"%s" from document type "%s"; %s',
                label or file_object.name, self, exception
            )
            raise


@python_2_unicode_compatible
class Document(models.Model):
    """
    Defines a single document with it's fields and properties
    Fields:
    * uuid - UUID of a document, universally Unique ID. An unique identifier
    generated for each document. No two documents can ever have the same UUID.
    This ID is generated automatically.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    document_type = models.ForeignKey(
        DocumentType, on_delete=models.CASCADE, related_name='documents',
        verbose_name=_('Document type')
    )
    label = models.CharField(
        blank=True, db_index=True, default='', max_length=255,
        help_text=_('The name of the document'), verbose_name=_('Label')
    )
    description = models.TextField(
        blank=True, default='', verbose_name=_('Description')
    )
    date_added = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Added')
    )
    language = models.CharField(
        blank=True, default=setting_language.value, max_length=8,
        verbose_name=_('Language')
    )
    in_trash = models.BooleanField(
        db_index=True, default=False, editable=False,
        verbose_name=_('In trash?')
    )
    # TODO: set editable to False
    deleted_date_time = models.DateTimeField(
        blank=True, editable=True, null=True,
        verbose_name=_('Date and time trashed')
    )
    is_stub = models.BooleanField(
        db_index=True, default=True, editable=False, help_text=_(
            'A document stub is a document with an entry on the database but '
            'no file uploaded. This could be an interrupted upload or a '
            'deferred upload via the API.'
        ), verbose_name=_('Is stub?')
    )

    objects = DocumentManager()
    passthrough = PassthroughManager()
    trash = TrashCanManager()

    def __str__(self):
        return self.label or ugettext('Document stub, id: %d') % self.pk

    def delete(self, *args, **kwargs):
        to_trash = kwargs.pop('to_trash', True)

        if not self.in_trash and to_trash:
            self.in_trash = True
            self.deleted_date_time = now()
            self.save()
        else:
            for version in self.versions.all():
                version.delete()

            return super(Document, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('documents:document_preview', args=(self.pk,))

    def natural_key(self):
        return (self.uuid,)
    natural_key.dependencies = ['documents.DocumentType']

    def save(self, *args, **kwargs):
        user = kwargs.pop('_user', None)
        _commit_events = kwargs.pop('_commit_events', True)
        new_document = not self.pk
        super(Document, self).save(*args, **kwargs)

        if new_document:
            if user:
                self.add_as_recent_document_for_user(user)
                event_document_create.commit(actor=user, target=self)
            else:
                event_document_create.commit(target=self)
        else:
            if _commit_events:
                event_document_properties_edit.commit(actor=user, target=self)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ('-date_added',)

    def add_as_recent_document_for_user(self, user):
        return RecentDocument.objects.add_document_for_user(user, self)

    def exists(self):
        """
        Returns a boolean value that indicates if the document's
        latest version file exists in storage
        """
        latest_version = self.latest_version
        if latest_version:
            return latest_version.exists()
        else:
            return False

    def invalidate_cache(self):
        for document_version in self.versions.all():
            document_version.invalidate_cache()

    def new_version(self, file_object, comment=None, _user=None):
        logger.info('Creating new document version for document: %s', self)

        document_version = DocumentVersion(
            document=self, comment=comment or '', file=File(file_object)
        )
        document_version.save(_user=_user)

        logger.info('New document version queued for document: %s', self)
        return document_version

    def open(self, *args, **kwargs):
        """
        Return a file descriptor to a document's file irrespective of
        the storage backend
        """
        return self.latest_version.open(*args, **kwargs)

    def restore(self):
        self.in_trash = False
        self.save()

    def save_to_file(self, *args, **kwargs):
        return self.latest_version.save_to_file(*args, **kwargs)

    def set_document_type(self, document_type, force=False, _user=None):
        has_changed = self.document_type != document_type

        self.document_type = document_type
        self.save()
        if has_changed or force:
            post_document_type_change.send(
                sender=self.__class__, instance=self
            )

            event_document_type_change.commit(actor=_user, target=self)
            if _user:
                self.add_as_recent_document_for_user(user=_user)

    @property
    def size(self):
        return self.latest_version.size

    # Compatibility methods

    @property
    def checksum(self):
        return self.latest_version.checksum

    @property
    def date_updated(self):
        return self.latest_version.timestamp

    # TODO: rename to file_encoding
    @property
    def file_mime_encoding(self):
        return self.latest_version.encoding

    @property
    def file_mimetype(self):
        return self.latest_version.mimetype

    @property
    def latest_version(self):
        return self.versions.order_by('timestamp').last()

    @property
    def page_count(self):
        return self.latest_version.page_count

    @property
    def pages(self):
        try:
            return self.latest_version.pages
        except AttributeError:
            # Document has no version yet
            return DocumentPage.objects.none()


class DeletedDocument(Document):
    objects = TrashCanManager()

    class Meta:
        proxy = True


@python_2_unicode_compatible
class DocumentVersion(models.Model):
    """
    Model that describes a document version and its properties
    Fields:
    * mimetype - File mimetype. MIME types are a standard way to describe the
    format of a file, in this case the file format of the document.
    Some examples: "text/plain" or "image/jpeg". Mayan uses this to determine
    how to render a document's file. More information:
    http://www.freeformatter.com/mime-types-list.html
    * encoding - File Encoding. The filesystem encoding of the document's
    file: binary 7-bit, binary 8-bit, text, base64, etc.
    * checksum - A hash/checkdigit/fingerprint generated from the document's
    binary data. Only identical documents will have the same checksum. If a
    document is modified after upload it's checksum will not match, used for
    detecting file tampering among other things.
    """
    _pre_open_hooks = {}
    _post_save_hooks = {}

    @classmethod
    def register_pre_open_hook(cls, order, func):
        cls._pre_open_hooks[order] = func

    @classmethod
    def register_post_save_hook(cls, order, func):
        cls._post_save_hooks[order] = func

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='versions',
        verbose_name=_('Document')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Timestamp')
    )
    comment = models.TextField(
        blank=True, default='', verbose_name=_('Comment')
    )

    # File related fields
    file = models.FileField(
        storage=storage_backend, upload_to=UUID_FUNCTION,
        verbose_name=_('File')
    )
    mimetype = models.CharField(
        blank=True, editable=False, max_length=255, null=True
    )
    encoding = models.CharField(
        blank=True, editable=False, max_length=64, null=True
    )
    checksum = models.CharField(
        blank=True, db_index=True, editable=False, max_length=64, null=True,
        verbose_name=_('Checksum')
    )

    class Meta:
        ordering = ('timestamp',)
        verbose_name = _('Document version')
        verbose_name_plural = _('Document version')

    def __str__(self):
        return self.get_rendered_string()

    def delete(self, *args, **kwargs):
        for page in self.pages.all():
            page.delete()

        self.file.storage.delete(self.file.name)

        return super(DocumentVersion, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('documents:document_version_view', args=(self.pk,))

    def get_rendered_string(self, preserve_extension=False):
        if preserve_extension:
            filename, extension = os.path.splitext(self.document.label)
            return '{} ({}){}'.format(
                filename, self.get_rendered_timestamp(), extension
            )
        else:
            return Template(
                '{{ instance.document }} - {{ instance.timestamp }}'
            ).render(context=Context({'instance': self}))

    def get_rendered_timestamp(self):
        return Template('{{ instance.timestamp }}').render(
            context=Context({'instance': self})
        )

    def save(self, *args, **kwargs):
        """
        Overloaded save method that updates the document version's checksum,
        mimetype, and page count when created
        """
        user = kwargs.pop('_user', None)
        new_document_version = not self.pk

        if new_document_version:
            logger.info('Creating new version for document: %s', self.document)

        try:
            with transaction.atomic():
                super(DocumentVersion, self).save(*args, **kwargs)

                for key in sorted(DocumentVersion._post_save_hooks):
                    DocumentVersion._post_save_hooks[key](
                        document_version=self
                    )

                if new_document_version:
                    # Only do this for new documents
                    self.update_checksum(save=False)
                    self.update_mimetype(save=False)
                    self.save()
                    self.update_page_count(save=False)
                    self.fix_orientation()

                    logger.info(
                        'New document version "%s" created for document: %s',
                        self, self.document
                    )

                    self.document.is_stub = False
                    if not self.document.label:
                        self.document.label = force_text(self.file)

                    self.document.save(_commit_events=False)
        except Exception as exception:
            logger.error(
                'Error creating new document version for document "%s"; %s',
                self.document, exception
            )
            raise
        else:
            if new_document_version:
                event_document_new_version.commit(
                    actor=user, target=self, action_object=self.document
                )
                post_version_upload.send(sender=DocumentVersion, instance=self)

                if tuple(self.document.versions.all()) == (self,):
                    post_document_created.send(
                        sender=Document, instance=self.document
                    )

    @property
    def cache_filename(self):
        return 'document-version-{}'.format(self.uuid)

    def exists(self):
        """
        Returns a boolean value that indicates if the document's file
        exists in storage. Returns True if the document's file is verified to
        be in the document storage. This is a diagnostic flag to help users
        detect if the storage has desynchronized (ie: Amazon's S3).
        """
        return self.file.storage.exists(self.file.name)

    def fix_orientation(self):
        for page in self.pages.all():
            degrees = page.detect_orientation()
            if degrees:
                Transformation.objects.add_for_model(
                    obj=page, transformation=TransformationRotate,
                    arguments='{{"degrees": {}}}'.format(360 - degrees)
                )

    def get_intermidiate_file(self):
        cache_filename = self.cache_filename
        logger.debug('Intermidiate filename: %s', cache_filename)

        if cache_storage_backend.exists(cache_filename):
            logger.debug('Intermidiate file "%s" found.', cache_filename)

            return cache_storage_backend.open(cache_filename)
        else:
            logger.debug('Intermidiate file "%s" not found.', cache_filename)

            try:
                converter = converter_class(file_object=self.open())
                pdf_file_object = converter.to_pdf()

                with cache_storage_backend.open(cache_filename, 'wb+') as file_object:
                    for chunk in pdf_file_object:
                        file_object.write(chunk)

                return cache_storage_backend.open(cache_filename)
            except InvalidOfficeFormat:
                return self.open()
            except Exception as exception:
                # Cleanup in case of error
                logger.error(
                    'Error creating intermediate file "%s"; %s.',
                    cache_filename, exception
                )
                cache_storage_backend.delete(cache_filename)
                raise

    def invalidate_cache(self):
        cache_storage_backend.delete(self.cache_filename)
        for page in self.pages.all():
            page.invalidate_cache()

    def open(self, raw=False):
        """
        Return a file descriptor to a document version's file irrespective of
        the storage backend
        """
        if raw:
            return self.file.storage.open(self.file.name)
        else:
            result = self.file.storage.open(self.file.name)
            for key in sorted(DocumentVersion._pre_open_hooks):
                result = DocumentVersion._pre_open_hooks[key](
                    file_object=result, document_version=self
                )

            return result

    @property
    def page_count(self):
        """
        The number of pages that the document posses.
        """
        return self.pages.count()

    def revert(self, _user=None):
        """
        Delete the subsequent versions after this one
        """
        logger.info(
            'Reverting to document document: %s to version: %s',
            self.document, self
        )

        event_document_version_revert.commit(actor=_user, target=self.document)
        for version in self.document.versions.filter(timestamp__gt=self.timestamp):
            version.delete()

    def save_to_file(self, filepath, buffer_size=1024 * 1024):
        """
        Save a copy of the document from the document storage backend
        to the local filesystem
        """
        input_descriptor = self.open()
        output_descriptor = open(filepath, 'wb')
        while True:
            copy_buffer = input_descriptor.read(buffer_size)
            if copy_buffer:
                output_descriptor.write(copy_buffer)
            else:
                break

        output_descriptor.close()
        input_descriptor.close()
        return filepath

    @property
    def size(self):
        if self.exists():
            return self.file.storage.size(self.file.name)
        else:
            return None

    def update_checksum(self, save=True):
        """
        Open a document version's file and update the checksum field using
        the user provided checksum function
        """
        if self.exists():
            source = self.open()
            self.checksum = force_text(HASH_FUNCTION(source.read()))
            source.close()
            if save:
                self.save()

    def update_mimetype(self, save=True):
        """
        Read a document verions's file and determine the mimetype by calling
        the get_mimetype wrapper
        """
        if self.exists():
            try:
                with self.open() as file_object:
                    self.mimetype, self.encoding = get_mimetype(
                        file_object=file_object
                    )
            except:
                self.mimetype = ''
                self.encoding = ''
            finally:
                if save:
                    self.save()

    def update_page_count(self, save=True):
        try:
            with self.open() as file_object:
                converter = converter_class(
                    file_object=file_object, mime_type=self.mimetype
                )
                detected_pages = converter.get_page_count()
        except PageCountError:
            # If converter backend doesn't understand the format,
            # use 1 as the total page count
            pass
        else:
            with transaction.atomic():
                self.pages.all().delete()

                for page_number in range(detected_pages):
                    DocumentPage.objects.create(
                        document_version=self, page_number=page_number + 1
                    )

            # TODO: is this needed anymore
            if save:
                self.save()

            return detected_pages

    @property
    def uuid(self):
        # Make cache UUID a mix of document UUID, version ID
        return '{}-{}'.format(self.document.uuid, self.pk)


@python_2_unicode_compatible
class DocumentTypeFilename(models.Model):
    """
    List of labels available to a specific document type for the
    quick rename functionality
    """
    document_type = models.ForeignKey(
        DocumentType, on_delete=models.CASCADE, related_name='filenames',
        verbose_name=_('Document type')
    )
    filename = models.CharField(
        db_index=True, max_length=128, verbose_name=_('Label')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))

    class Meta:
        ordering = ('filename',)
        unique_together = ('document_type', 'filename')
        verbose_name = _('Quick label')
        verbose_name_plural = _('Quick labels')

    def __str__(self):
        return self.filename


@python_2_unicode_compatible
class DocumentPage(models.Model):
    """
    Model that describes a document version page
    """
    document_version = models.ForeignKey(
        DocumentVersion, on_delete=models.CASCADE, related_name='pages',
        verbose_name=_('Document version')
    )
    page_number = models.PositiveIntegerField(
        db_index=True, default=1, editable=False,
        verbose_name=_('Page number')
    )

    def __str__(self):
        return _(
            'Page %(page_num)d out of %(total_pages)d of %(document)s'
        ) % {
            'document': force_text(self.document),
            'page_num': self.page_number,
            'total_pages': self.document_version.pages.count()
        }

    def delete(self, *args, **kwargs):
        self.invalidate_cache()
        super(DocumentPage, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('documents:document_page_view', args=(self.pk,))

    class Meta:
        ordering = ('page_number',)
        verbose_name = _('Document page')
        verbose_name_plural = _('Document pages')

    @property
    def cache_filename(self):
        return 'page-cache-{}'.format(self.uuid)

    @property
    def document(self):
        return self.document_version.document

    def detect_orientation(self):
        with self.document_version.open() as file_object:
            converter = converter_class(
                file_object=file_object,
                mime_type=self.document_version.mimetype
            )
            return converter.detect_orientation(
                page_number=self.page_number
            )

    def generate_image(self, *args, **kwargs):
        # Convert arguments into transformations
        transformations = kwargs.get('transformations', [])

        # Set sensible defaults if the argument is not specified or if the
        # argument is None
        size = kwargs.get('size', setting_display_size.value) or setting_display_size.value
        rotation = kwargs.get('rotation', DEFAULT_ROTATION) or DEFAULT_ROTATION
        zoom_level = kwargs.get('zoom', DEFAULT_ZOOM_LEVEL) or DEFAULT_ZOOM_LEVEL

        if zoom_level < setting_zoom_min_level.value:
            zoom_level = setting_zoom_min_level.value

        if zoom_level > setting_zoom_max_level.value:
            zoom_level = setting_zoom_max_level.value

        # Generate transformation hash

        transformation_list = []

        # Stored transformations first
        for stored_transformation in Transformation.objects.get_for_model(self, as_classes=True):
            transformation_list.append(stored_transformation)

        # Interactive transformations second
        for transformation in transformations:
            transformation_list.append(transformation)

        if rotation:
            transformation_list.append(
                TransformationRotate(degrees=rotation)
            )

        if size:
            transformation_list.append(
                TransformationResize(
                    **dict(zip(('width', 'height'), (size.split('x'))))
                )
            )

        if zoom_level:
            transformation_list.append(TransformationZoom(percent=zoom_level))

        cache_filename = '{}-{}'.format(
            self.cache_filename, BaseTransformation.combine(transformation_list)
        )

        # Check is transformed image is available
        logger.debug('transformations cache filename: %s', cache_filename)

        if not setting_disable_transformed_image_cache.value and cache_storage_backend.exists(cache_filename):
            logger.debug(
                'transformations cache file "%s" found', cache_filename
            )
        else:
            logger.debug(
                'transformations cache file "%s" not found', cache_filename
            )
            image = self.get_image(transformations=transformation_list)
            with cache_storage_backend.open(cache_filename, 'wb+') as file_object:
                file_object.write(image.getvalue())

            self.cached_images.create(filename=cache_filename)

        return cache_filename

    def get_image(self, transformations=None):
        cache_filename = self.cache_filename
        logger.debug('Page cache filename: %s', cache_filename)

        if not setting_disable_base_image_cache.value and cache_storage_backend.exists(cache_filename):
            logger.debug('Page cache file "%s" found', cache_filename)
            converter = converter_class(
                file_object=cache_storage_backend.open(cache_filename)
            )

            converter.seek(0)
        else:
            logger.debug('Page cache file "%s" not found', cache_filename)

            try:
                converter = converter_class(
                    file_object=self.document_version.get_intermidiate_file()
                )
                converter.seek(page_number=self.page_number - 1)

                page_image = converter.get_page()

                with cache_storage_backend.open(cache_filename, 'wb+') as file_object:
                    file_object.write(page_image.getvalue())
            except Exception as exception:
                # Cleanup in case of error
                logger.error(
                    'Error creating page cache file "%s"; %s',
                    cache_filename, exception
                )
                cache_storage_backend.delete(cache_filename)
                raise

        for transformation in transformations:
            converter.transform(transformation=transformation)

        return converter.get_page()

    def invalidate_cache(self):
        cache_storage_backend.delete(self.cache_filename)
        for cached_image in self.cached_images.all():
            cached_image.delete()

    @property
    def siblings(self):
        return DocumentPage.objects.filter(
            document_version=self.document_version
        )

    @property
    def uuid(self):
        """
        Make cache UUID a mix of version ID and page ID to avoid using stale
        images
        """
        return '{}-{}'.format(self.document_version.uuid, self.pk)


class DocumentPageCachedImage(models.Model):
    document_page = models.ForeignKey(
        DocumentPage, on_delete=models.CASCADE, related_name='cached_images',
        verbose_name=_('Document page')
    )
    filename = models.CharField(max_length=128, verbose_name=_('Filename'))

    class Meta:
        verbose_name = _('Document page cached image')
        verbose_name_plural = _('Document page cached images')

    def delete(self, *args, **kwargs):
        cache_storage_backend.delete(self.filename)
        return super(DocumentPageCachedImage, self).delete(*args, **kwargs)


class DocumentPageResult(DocumentPage):
    class Meta:
        ordering = ('document_version__document', 'page_number')
        proxy = True
        verbose_name = _('Document page')
        verbose_name_plural = _('Document pages')


@python_2_unicode_compatible
class RecentDocument(models.Model):
    """
    Keeps a list of the n most recent accessed or created document for
    a given user
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_index=True, editable=False,
        on_delete=models.CASCADE, verbose_name=_('User')
    )
    document = models.ForeignKey(
        Document, editable=False, on_delete=models.CASCADE,
        verbose_name=_('Document')
    )
    datetime_accessed = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_('Accessed')
    )

    objects = RecentDocumentManager()

    def __str__(self):
        return force_text(self.document)

    def natural_key(self):
        return self.document.natural_key() + self.user.natural_key()
    natural_key.dependencies = ['documents.Document', settings.AUTH_USER_MODEL]

    class Meta:
        ordering = ('-datetime_accessed',)
        verbose_name = _('Recent document')
        verbose_name_plural = _('Recent documents')


@python_2_unicode_compatible
class DuplicatedDocument(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='duplicates',
        verbose_name=_('Document')
    )
    documents = models.ManyToManyField(
        Document, verbose_name=_('Duplicated documents')
    )
    datetime_added = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Added')
    )

    objects = DuplicatedDocumentManager()

    def __str__(self):
        return force_text(self.document)

    class Meta:
        verbose_name = _('Duplicated document')
        verbose_name_plural = _('Duplicated documents')
