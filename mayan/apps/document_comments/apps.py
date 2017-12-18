from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from common import MayanAppConfig, menu_facet, menu_object, menu_sidebar
from documents.search import document_page_search, document_search
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .links import (
    link_comment_add, link_comment_delete, link_comments_for_document
)
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)


class DocumentCommentsApp(MayanAppConfig):
    app_namespace = 'comments'
    app_url = 'comments'
    has_tests = True
    name = 'document_comments'
    verbose_name = _('Document comments')

    def ready(self):
        super(DocumentCommentsApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        Comment = self.get_model('Comment')

        ModelPermission.register(
            model=Document, permissions=(
                permission_comment_create, permission_comment_delete,
                permission_comment_view
            )
        )

        SourceColumn(source=Comment, label=_('Date'), attribute='submit_date')
        SourceColumn(
            source=Comment, label=_('User'),
            func=lambda context: context['object'].user.get_full_name() if context['object'].user.get_full_name() else context['object'].user
        )
        SourceColumn(source=Comment, label=_('Comment'), attribute='comment')

        document_page_search.add_model_field(
            field='document_version__document__comments__comment',
            label=_('Comments')
        )
        document_search.add_model_field(
            field='comments__comment',
            label=_('Comments')
        )

        menu_sidebar.bind_links(
            links=(link_comment_add,),
            sources=(
                'comments:comments_for_document', 'comments:comment_add',
                'comments:comment_delete', 'comments:comment_multiple_delete'
            )
        )
        menu_object.bind_links(
            links=(link_comment_delete,), sources=(Comment,)
        )
        menu_facet.bind_links(
            links=(link_comments_for_document,), sources=(Document,)
        )
