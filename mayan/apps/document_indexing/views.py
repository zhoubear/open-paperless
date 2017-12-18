from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.views import (
    AssignRemoveView, FormView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectEditView, SingleObjectListView
)
from documents.models import Document, DocumentType
from documents.permissions import permission_document_view
from documents.views import DocumentListView

from .forms import IndexListForm, IndexTemplateNodeForm
from .models import (
    DocumentIndexInstanceNode, Index, IndexInstance, IndexInstanceNode,
    IndexTemplateNode
)
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit, permission_document_indexing_rebuild,
    permission_document_indexing_view
)
from .tasks import task_rebuild_index
from .widgets import node_tree


# Setup views
class SetupIndexCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create index')}
    fields = ('label', 'slug', 'enabled')
    model = Index
    post_action_redirect = reverse_lazy('indexing:index_setup_list')
    view_permission = permission_document_indexing_create


class SetupIndexDeleteView(SingleObjectDeleteView):
    model = Index
    post_action_redirect = reverse_lazy('indexing:index_setup_list')
    object_permission = permission_document_indexing_delete

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the index: %s?') % self.get_object(),
        }


class SetupIndexEditView(SingleObjectEditView):
    fields = ('label', 'slug', 'enabled')
    model = Index
    post_action_redirect = reverse_lazy('indexing:index_setup_list')
    object_permission = permission_document_indexing_edit

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit index: %s') % self.get_object(),
        }


class SetupIndexListView(SingleObjectListView):
    model = Index
    object_permission = permission_document_indexing_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Indexes'),
        }


class SetupIndexDocumentTypesView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available document types')
    object_permission = permission_document_indexing_edit
    right_list_title = _('Document types linked')

    def add(self, item):
        self.get_object().document_types.add(item)

    def get_document_queryset(self):
        return AccessControlList.objects.filter_by_access(
            permission_document_view, self.request.user,
            queryset=DocumentType.objects.all()
        )

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _(
                'Document types linked to index: %s'
            ) % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(Index, pk=self.kwargs['pk'])

    def left_list(self):
        return AssignRemoveView.generate_choices(
            self.get_document_queryset().exclude(
                id__in=self.get_object().document_types.all()
            )
        )

    def remove(self, item):
        self.get_object().document_types.remove(item)

    def right_list(self):
        return AssignRemoveView.generate_choices(
            self.get_document_queryset() & self.get_object().document_types.all()
        )


class SetupIndexTreeTemplateListView(SingleObjectListView):
    object_permission = permission_document_indexing_edit

    def get_extra_context(self):
        return {
            'hide_object': True,
            'index': self.get_index(),
            'navigation_object_list': ('index',),
            'title': _('Tree template nodes for index: %s') % self.get_index(),
        }

    def get_index(self):
        return get_object_or_404(Index, pk=self.kwargs['pk'])

    def get_object_list(self):
        return self.get_index().template_root.get_descendants(
            include_self=True
        )


class TemplateNodeCreateView(SingleObjectCreateView):
    form_class = IndexTemplateNodeForm
    model = IndexTemplateNode

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_indexing_edit, user=request.user,
            obj=self.get_parent_node().index
        )

        return super(
            TemplateNodeCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'index': self.get_parent_node().index,
            'navigation_object_list': ('index',),
            'title': _('Create child node of: %s') % self.get_parent_node(),
        }

    def get_initial(self):
        parent_node = self.get_parent_node()
        return {
            'index': parent_node.index, 'parent': parent_node
        }

    def get_parent_node(self):
        return get_object_or_404(IndexTemplateNode, pk=self.kwargs['pk'])


class TemplateNodeDeleteView(SingleObjectDeleteView):
    model = IndexTemplateNode
    object_permission = permission_document_indexing_edit
    object_permission_related = 'index'

    def get_extra_context(self):
        return {
            'index': self.get_object().index,
            'navigation_object_list': ('index', 'node'),
            'node': self.get_object(),
            'title': _(
                'Delete the index template node: %s?'
            ) % self.get_object(),
        }

    def get_post_action_redirect(self):
        return reverse(
            'indexing:index_setup_view', args=(self.get_object().index.pk,)
        )


class TemplateNodeEditView(SingleObjectEditView):
    form_class = IndexTemplateNodeForm
    model = IndexTemplateNode
    object_permission = permission_document_indexing_edit
    object_permission_related = 'index'

    def get_extra_context(self):
        return {
            'index': self.get_object().index,
            'navigation_object_list': ('index', 'node'),
            'node': self.get_object(),
            'title': _(
                'Edit the index template node: %s?'
            ) % self.get_object(),
        }

    def get_post_action_redirect(self):
        return reverse(
            'indexing:index_setup_view', args=(self.get_object().index.pk,)
        )


class IndexListView(SingleObjectListView):
    object_permission = permission_document_indexing_view
    queryset = IndexInstance.objects.filter(enabled=True)

    def get_extra_context(self):
        return {
            'hide_links': True,
            'title': _('Indexes'),
        }


class IndexInstanceNodeView(DocumentListView):
    template_name = 'document_indexing/node_details.html'

    def dispatch(self, request, *args, **kwargs):
        self.index_instance_node = get_object_or_404(
            IndexInstanceNode, pk=self.kwargs['pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_document_indexing_view,
            user=request.user, obj=self.index_instance_node.index()
        )

        if self.index_instance_node:
            if self.index_instance_node.index_template_node.link_documents:
                return super(IndexInstanceNodeView, self).dispatch(
                    request, *args, **kwargs
                )

        return SingleObjectListView.dispatch(self, request, *args, **kwargs)

    def get_document_queryset(self):
        if self.index_instance_node:
            if self.index_instance_node.index_template_node.link_documents:
                return self.index_instance_node.documents.all()

    def get_extra_context(self):
        context = super(IndexInstanceNodeView, self).get_extra_context()
        context.update(
            {
                'object': self.index_instance_node,
                'navigation': mark_safe(
                    _('Navigation: %s') % node_tree(
                        node=self.index_instance_node, user=self.request.user
                    )
                ),
                'title': _(
                    'Contents for index: %s'
                ) % self.index_instance_node.get_full_path(),
            }
        )

        if self.index_instance_node and not self.index_instance_node.index_template_node.link_documents:
            context.update(
                {
                    'hide_object': True,
                    'list_as_items': False,
                }
            )

        return context

    def get_object_list(self):
        if self.index_instance_node:
            if self.index_instance_node.index_template_node.link_documents:
                return super(IndexInstanceNodeView, self).get_object_list()
            else:
                self.object_permission = None
                return self.index_instance_node.get_children().order_by(
                    'value'
                )
        else:
            self.object_permission = None
            return IndexInstanceNode.objects.none()


class DocumentIndexNodeListView(SingleObjectListView):
    """
    Show a list of indexes where the current document can be found
    """

    object_permission = permission_document_indexing_view
    object_permission_related = 'index'

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=self.get_document()
        )

        return super(
            DocumentIndexNodeListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_document(),
            'title': _(
                'Indexes nodes containing document: %s'
            ) % self.get_document(),
        }

    def get_object_list(self):
        return DocumentIndexInstanceNode.objects.get_for(self.get_document())


class RebuildIndexesView(FormView):
    extra_context = {
        'title': _('Rebuild indexes'),
    }
    form_class = IndexListForm
    view_permission = permission_document_indexing_rebuild

    def form_valid(self, form):
        for index in form.cleaned_data['indexes']:
            task_rebuild_index.apply_async(
                kwargs=dict(index_id=index.pk)
            )

        messages.success(self.request, _('Index rebuild queued successfully.'))

        return super(RebuildIndexesView, self).form_valid(form=form)

    def get_post_action_redirect(self):
        return reverse('common:tools_list')
