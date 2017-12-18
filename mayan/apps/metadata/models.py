from __future__ import unicode_literals

import shlex

from django.core.exceptions import ValidationError
from django.db import models
from django.template import Context, Template
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from documents.models import Document, DocumentType

from .classes import MetadataLookup
from .managers import DocumentTypeMetadataTypeManager, MetadataTypeManager
from .settings import setting_available_parsers, setting_available_validators


def validation_choices():
    return zip(
        setting_available_validators.value,
        setting_available_validators.value
    )


def parser_choices():
    return zip(
        setting_available_parsers.value,
        setting_available_parsers.value
    )


@python_2_unicode_compatible
class MetadataType(models.Model):
    """
    Define a type of metadata
    """

    name = models.CharField(
        max_length=48,
        help_text=_(
            'Name used by other apps to reference this value. '
            'Do not use python reserved words, or spaces.'
        ),
        unique=True, verbose_name=_('Name')
    )
    label = models.CharField(max_length=48, verbose_name=_('Label'))
    default = models.CharField(
        blank=True, max_length=128, null=True,
        help_text=_(
            'Enter a template to render. '
            'Use Django\'s default templating language '
            '(https://docs.djangoproject.com/en/1.7/ref/templates/builtins/)'
        ),
        verbose_name=_('Default')
    )
    lookup = models.TextField(
        blank=True, null=True,
        help_text=_(
            'Enter a template to render. '
            'Must result in a comma delimited string. '
            'Use Django\'s default templating language '
            '(https://docs.djangoproject.com/en/1.7/ref/templates/builtins/).'
        ),
        verbose_name=_('Lookup')
    )
    validation = models.CharField(
        blank=True, choices=validation_choices(),
        help_text=_(
            'The validator will reject data entry if the value entered does '
            'not conform to the expected format.'
        ), max_length=64, verbose_name=_('Validator')
    )
    parser = models.CharField(
        blank=True, choices=parser_choices(), help_text=_(
            'The parser will reformat the value entered to conform to the '
            'expected format.'
        ), max_length=64, verbose_name=_('Parser')
    )

    objects = MetadataTypeManager()

    def __str__(self):
        return self.label

    def natural_key(self):
        return (self.name,)

    class Meta:
        ordering = ('label',)
        verbose_name = _('Metadata type')
        verbose_name_plural = _('Metadata types')

    @staticmethod
    def comma_splitter(string):
        splitter = shlex.shlex(string.encode('utf-8'), posix=True)
        splitter.whitespace = ','.encode('utf-8')
        splitter.whitespace_split = True
        splitter.commenters = ''.encode('utf-8')
        return [force_text(e) for e in splitter]

    def get_default_value(self):
        template = Template(self.default)
        context = Context()
        return template.render(context=context)

    def get_lookup_values(self):
        template = Template(self.lookup)
        context = Context(MetadataLookup.get_as_context())
        return MetadataType.comma_splitter(template.render(context=context))

    def get_required_for(self, document_type):
        return document_type.metadata.filter(
            required=True, metadata_type=self
        ).exists()

    def validate_value(self, document_type, value):
        # Check default
        if not value and self.default:
            value = self.get_default_value()

        if not value and self.get_required_for(document_type=document_type):
            raise ValidationError(
                _('"%s" is required for this document type.') % self.label
            )

        if self.lookup:
            lookup_options = self.get_lookup_values()

            if value and value not in lookup_options:
                raise ValidationError(
                    _('Value is not one of the provided options.')
                )

        if self.validation:
            validator = import_string(self.validation)()
            validator.validate(value)

        if self.parser:
            parser = import_string(self.parser)()
            value = parser.parse(value)

        return value


@python_2_unicode_compatible
class DocumentMetadata(models.Model):
    """
    Link a document to a specific instance of a metadata type with it's
    current value
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='metadata',
        verbose_name=_('Document')
    )
    metadata_type = models.ForeignKey(
        MetadataType, on_delete=models.CASCADE, verbose_name=_('Type')
    )
    value = models.CharField(
        blank=True, db_index=True, max_length=255, null=True,
        verbose_name=_('Value')
    )

    def __str__(self):
        return force_text(self.metadata_type)

    def delete(self, enforce_required=True, *args, **kwargs):
        """
        enforce_required prevents deletion of required metadata at the
        model level. It used set to False when deleting document metadata
        on document type change.
        """
        if enforce_required and self.metadata_type.pk in self.document.document_type.metadata.filter(required=True).values_list('metadata_type', flat=True):
            raise ValidationError(
                _('Metadata type is required for this document type.')
            )

        return super(DocumentMetadata, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.metadata_type.pk not in self.document.document_type.metadata.values_list('metadata_type', flat=True):
            raise ValidationError(
                _('Metadata type is not valid for this document type.')
            )

        return super(DocumentMetadata, self).save(*args, **kwargs)

    def clean_fields(self, *args, **kwargs):
        super(DocumentMetadata, self).clean_fields(*args, **kwargs)

        self.value = self.metadata_type.validate_value(
            document_type=self.document.document_type, value=self.value
        )

    class Meta:
        unique_together = ('document', 'metadata_type')
        verbose_name = _('Document metadata')
        verbose_name_plural = _('Document metadata')

    @property
    def is_required(self):
        return self.metadata_type.get_required_for(
            document_type=self.document.document_type
        )


@python_2_unicode_compatible
class DocumentTypeMetadataType(models.Model):
    document_type = models.ForeignKey(
        DocumentType, on_delete=models.CASCADE, related_name='metadata',
        verbose_name=_('Document type')
    )
    metadata_type = models.ForeignKey(
        MetadataType, on_delete=models.CASCADE,
        verbose_name=_('Metadata type')
    )
    required = models.BooleanField(default=False, verbose_name=_('Required'))

    objects = DocumentTypeMetadataTypeManager()

    def __str__(self):
        return force_text(self.metadata_type)

    class Meta:
        unique_together = ('document_type', 'metadata_type')
        verbose_name = _('Document type metadata type options')
        verbose_name_plural = _('Document type metadata types options')
