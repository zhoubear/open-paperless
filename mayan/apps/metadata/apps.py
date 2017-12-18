from __future__ import unicode_literals

import logging

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import post_delete, post_save
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from common import (
    MayanAppConfig, menu_facet, menu_multi_item, menu_object, menu_secondary,
    menu_setup, menu_sidebar
)
from common.classes import ModelAttribute, Filter
from common.widgets import two_state_template
from documents.search import document_page_search, document_search
from documents.signals import post_document_type_change
from documents.permissions import permission_document_view
from mayan.celery import app
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .classes import DocumentMetadataHelper
from .handlers import (
    handler_index_document, post_document_type_metadata_type_add,
    post_document_type_metadata_type_delete,
    post_document_type_change_metadata
)
from .links import (
    link_metadata_add, link_metadata_edit, link_metadata_multiple_add,
    link_metadata_multiple_edit, link_metadata_multiple_remove,
    link_metadata_remove, link_metadata_view,
    link_setup_document_type_metadata_types, link_setup_metadata_type_create,
    link_setup_metadata_type_delete, link_setup_metadata_type_document_types,
    link_setup_metadata_type_edit, link_setup_metadata_type_list,
)
from .permissions import (
    permission_metadata_document_add, permission_metadata_document_edit,
    permission_metadata_document_remove, permission_metadata_document_view
)
from .queues import *  # NOQA
from .search import metadata_type_search  # NOQA
from .widgets import get_metadata_string

logger = logging.getLogger(__name__)


class MetadataApp(MayanAppConfig):
    has_tests = True
    name = 'metadata'
    verbose_name = _('Metadata')

    def ready(self):
        super(MetadataApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentPageResult = apps.get_model(
            app_label='documents', model_name='DocumentPageResult'
        )

        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        DocumentMetadata = self.get_model('DocumentMetadata')
        DocumentTypeMetadataType = self.get_model('DocumentTypeMetadataType')
        MetadataType = self.get_model('MetadataType')

        APIEndPoint(app=self, version_string='2')

        Document.add_to_class(
            'metadata_value_of', DocumentMetadataHelper.constructor
        )

        Filter(
            label=_('Documents missing required metadata'),
            slug='documents-no-required-metadata',
            filter_kwargs=[
                {
                    'document_type__metadata__required': True,
                },
                {
                    'metadata__value__isnull': True
                },
                {
                    'is_stub': False
                }
            ], model=Document, object_permission=permission_document_view,
            hide_links=True
        )

        Filter(
            label=_('Documents missing optional metadata'),
            slug='documents-no-optional-metadata',
            filter_kwargs=[
                {
                    'document_type__metadata__required': False,
                },
                {
                    'metadata__value__isnull': True
                },
                {
                    'is_stub': False
                }
            ], model=Document, object_permission=permission_document_view,
            hide_links=True
        )

        ModelAttribute(
            Document, 'metadata', type_name='related',
            description=_(
                'Queryset containing a MetadataType instance reference and a '
                'value for that metadata type'
            )
        )
        ModelAttribute(
            Document, 'metadata__metadata_type__name',
            label=_('Metadata type name'), type_name='query'
        )
        ModelAttribute(
            Document, 'metadata__value', label=_('Metadata type value'),
            type_name='query'
        )
        ModelAttribute(
            Document, 'metadata_value_of', label=_('Value of a metadata'),
            description=_(
                'Return the value of a specific document metadata'
            ),
            type_name=['property', 'indexing']
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_metadata_document_add,
                permission_metadata_document_edit,
                permission_metadata_document_remove,
                permission_metadata_document_view,
            )
        )

        SourceColumn(
            source=Document, label=_('Metadata'),
            func=lambda context: get_metadata_string(context['object'])
        )

        SourceColumn(
            source=DocumentPageResult, label=_('Metadata'),
            func=lambda context: get_metadata_string(
                context['object'].document
            )
        )

        SourceColumn(
            source=DocumentMetadata, label=_('Value'),
            attribute='value'
        )
        SourceColumn(
            source=DocumentMetadata, label=_('Required'),
            func=lambda context: two_state_template(
                context['object'].is_required
            )
        )

        app.conf.CELERY_QUEUES.append(
            Queue('metadata', Exchange('metadata'), routing_key='metadata'),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'metadata.tasks.task_remove_metadata_type': {
                    'queue': 'metadata'
                },
                'metadata.tasks.task_add_required_metadata_type': {
                    'queue': 'metadata'
                },
            }
        )

        document_search.add_model_field(
            field='metadata__metadata_type__name', label=_('Metadata type')
        )
        document_search.add_model_field(
            field='metadata__value', label=_('Metadata value')
        )

        document_page_search.add_model_field(
            field='document_version__document__metadata__metadata_type__name',
            label=_('Metadata type')
        )
        document_page_search.add_model_field(
            field='document_version__document__metadata__value',
            label=_('Metadata value')
        )

        menu_facet.bind_links(links=(link_metadata_view,), sources=(Document,))
        menu_multi_item.bind_links(
            links=(
                link_metadata_multiple_add, link_metadata_multiple_edit,
                link_metadata_multiple_remove
            ), sources=(Document,)
        )
        menu_object.bind_links(
            links=(
                link_setup_document_type_metadata_types,
            ), sources=(DocumentType,)
        )
        menu_object.bind_links(
            links=(
                link_setup_metadata_type_edit,
                link_setup_metadata_type_document_types,
                link_setup_metadata_type_delete
            ), sources=(MetadataType,)
        )
        menu_secondary.bind_links(
            links=(
                link_setup_metadata_type_list,
                link_setup_metadata_type_create
            ), sources=(
                MetadataType, 'metadata:setup_metadata_type_list',
                'metadata:setup_metadata_type_create'
            )
        )
        menu_setup.bind_links(links=(link_setup_metadata_type_list,))
        menu_sidebar.bind_links(
            links=(
                link_metadata_add, link_metadata_edit, link_metadata_remove
            ), sources=(
                'metadata:metadata_add', 'metadata:metadata_edit',
                'metadata:metadata_remove', 'metadata:metadata_view'
            )
        )

        post_delete.connect(
            post_document_type_metadata_type_delete,
            dispatch_uid='metadata_post_document_type_metadata_type_delete',
            sender=DocumentTypeMetadataType
        )
        post_document_type_change.connect(
            post_document_type_change_metadata,
            dispatch_uid='metadata_post_document_type_change_metadata',
            sender=Document
        )
        post_save.connect(
            post_document_type_metadata_type_add,
            dispatch_uid='metadata_post_document_type_metadata_type_add',
            sender=DocumentTypeMetadataType
        )

        # Index updating

        post_delete.connect(
            handler_index_document,
            dispatch_uid='metadata_handler_index_document_delete',
            sender=DocumentMetadata
        )
        post_save.connect(
            handler_index_document,
            dispatch_uid='metadata_handler_index_document_save',
            sender=DocumentMetadata
        )
