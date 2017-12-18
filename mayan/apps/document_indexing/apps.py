from __future__ import absolute_import, unicode_literals

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import post_delete, pre_delete
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from acls.links import link_acl_list
from acls.permissions import permission_acl_edit, permission_acl_view

from common import (
    MayanAppConfig, menu_facet, menu_main, menu_object, menu_secondary,
    menu_setup, menu_tools
)
from common.widgets import two_state_template
from documents.signals import post_document_created, post_initial_document_type
from mayan.celery import app
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .handlers import (
    create_default_document_index, handler_delete_empty,
    handler_index_document, handler_remove_document
)
from .links import (
    link_document_index_list, link_index_main_menu, link_index_setup,
    link_index_setup_create, link_index_setup_document_types,
    link_index_setup_delete, link_index_setup_edit, link_index_setup_list,
    link_index_setup_view, link_rebuild_index_instances,
    link_template_node_create, link_template_node_delete,
    link_template_node_edit
)
from .licenses import *  # NOQA
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit, permission_document_indexing_view
)
from .queues import *  # NOQA
from .widgets import get_instance_link, index_instance_item_link, node_level


class DocumentIndexingApp(MayanAppConfig):
    app_namespace = 'indexing'
    app_url = 'indexing'
    has_tests = True
    name = 'document_indexing'
    verbose_name = _('Document indexing')

    def ready(self):
        super(DocumentIndexingApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        DocumentIndexInstanceNode = self.get_model('DocumentIndexInstanceNode')

        Index = self.get_model('Index')
        IndexInstance = self.get_model('IndexInstance')
        IndexInstanceNode = self.get_model('IndexInstanceNode')
        IndexTemplateNode = self.get_model('IndexTemplateNode')

        ModelPermission.register(
            model=Index, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_document_indexing_create,
                permission_document_indexing_delete,
                permission_document_indexing_edit,
                permission_document_indexing_view,
            )
        )

        SourceColumn(source=Index, label=_('Label'), attribute='label')
        SourceColumn(source=Index, label=_('Slug'), attribute='slug')
        SourceColumn(
            source=Index, label=_('Enabled'),
            func=lambda context: two_state_template(context['object'].enabled)
        )

        SourceColumn(
            source=IndexInstance, label=_('Total levels'),
            func=lambda context: context[
                'object'
            ].instance_root.get_descendants_count()
        )
        SourceColumn(
            source=IndexInstance, label=_('Total documents'),
            func=lambda context: context[
                'object'
            ].instance_root.get_descendants_document_count(
                user=context['request'].user
            )
        )
        SourceColumn(
            source=IndexInstance, label=_('Document types'),
            attribute='get_document_types_names'
        )

        SourceColumn(
            source=IndexTemplateNode, label=_('Level'),
            func=lambda context: node_level(context['object'])
        )
        SourceColumn(
            source=IndexTemplateNode, label=_('Enabled'),
            func=lambda context: two_state_template(context['object'].enabled)
        )
        SourceColumn(
            source=IndexTemplateNode, label=_('Has document links?'),
            func=lambda context: two_state_template(
                context['object'].link_documents
            )
        )

        SourceColumn(
            source=IndexInstanceNode, label=_('Level'),
            func=lambda context: index_instance_item_link(context['object'])
        )
        SourceColumn(
            source=IndexInstanceNode, label=_('Levels'),
            func=lambda context: context['object'].get_descendants_count()
        )
        SourceColumn(
            source=IndexInstanceNode, label=_('Documents'),
            func=lambda context: context[
                'object'
            ].get_descendants_document_count(
                user=context['request'].user
            )
        )

        SourceColumn(
            source=DocumentIndexInstanceNode, label=_('Level'),
            func=lambda context: get_instance_link(
                index_instance_node=context['object'],
            )
        )
        SourceColumn(
            source=DocumentIndexInstanceNode, label=_('Levels'),
            func=lambda context: context['object'].get_descendants_count()
        )
        SourceColumn(
            source=DocumentIndexInstanceNode, label=_('Documents'),
            func=lambda context: context[
                'object'
            ].get_descendants_document_count(
                user=context['request'].user
            )
        )

        app.conf.CELERY_QUEUES.append(
            Queue('indexing', Exchange('indexing'), routing_key='indexing'),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'document_indexing.tasks.task_delete_empty': {
                    'queue': 'indexing'
                },
                'document_indexing.tasks.task_remove_document': {
                    'queue': 'indexing'
                },
                'document_indexing.tasks.task_index_document': {
                    'queue': 'indexing'
                },
                'document_indexing.tasks.task_rebuild_index': {
                    'queue': 'tools'
                },
            }
        )

        menu_facet.bind_links(
            links=(link_document_index_list,), sources=(Document,)
        )
        menu_object.bind_links(
            links=(
                link_index_setup_edit, link_index_setup_view,
                link_index_setup_document_types, link_acl_list,
                link_index_setup_delete
            ), sources=(Index,)
        )
        menu_object.bind_links(
            links=(
                link_template_node_create, link_template_node_edit,
                link_template_node_delete
            ), sources=(IndexTemplateNode,)
        )
        menu_main.bind_links(links=(link_index_main_menu,), position=98)
        menu_secondary.bind_links(
            links=(link_index_setup_list, link_index_setup_create),
            sources=(
                Index, 'indexing:index_setup_list',
                'indexing:index_setup_create'
            )
        )
        menu_setup.bind_links(links=(link_index_setup,))
        menu_tools.bind_links(links=(link_rebuild_index_instances,))

        post_delete.connect(
            handler_delete_empty, dispatch_uid='handler_delete_empty',
            sender=Document
        )
        pre_delete.connect(
            handler_remove_document, dispatch_uid='handler_remove_document',
            sender=Document
        )
        post_document_created.connect(
            handler_index_document,
            dispatch_uid='handler_index_document', sender=Document
        )
        post_initial_document_type.connect(
            create_default_document_index,
            dispatch_uid='create_default_document_index', sender=DocumentType
        )
