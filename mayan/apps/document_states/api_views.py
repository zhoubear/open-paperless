from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document, DocumentType
from documents.permissions import permission_document_type_view
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Workflow
from .permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_view
)
from .serializers import (
    NewWorkflowDocumentTypeSerializer, WorkflowDocumentTypeSerializer,
    WorkflowInstanceSerializer, WorkflowInstanceLogEntrySerializer,
    WorkflowSerializer, WorkflowStateSerializer, WorkflowTransitionSerializer,
    WritableWorkflowInstanceLogEntrySerializer, WritableWorkflowSerializer,
    WritableWorkflowTransitionSerializer
)


class APIDocumentTypeWorkflowListView(generics.ListAPIView):
    serializer_class = WorkflowSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the document type workflows.
        """
        return super(
            APIDocumentTypeWorkflowListView, self
        ).get(*args, **kwargs)

    def get_document_type(self):
        document_type = get_object_or_404(DocumentType, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=document_type
        )

        return document_type

    def get_queryset(self):
        return self.get_document_type().workflows.all()


class APIWorkflowDocumentTypeList(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_document_type_view,),
    }

    def get(self, *args, **kwargs):
        """
        Returns a list of all the document types attached to a workflow.
        """

        return super(APIWorkflowDocumentTypeList, self).get(*args, **kwargs)

    def get_queryset(self):
        """
        This view returns a list of document types that belong to a workflow
        RESEARCH: Could the documents.api_views.APIDocumentTypeList class
        be subclasses for this?
        """

        return self.get_workflow().document_types.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowDocumentTypeSerializer
        elif self.request.method == 'POST':
            return NewWorkflowDocumentTypeSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """

        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        """
        Retrieve the parent workflow of the workflow document type.
        Perform custom permission and access check.
        """

        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def post(self, request, *args, **kwargs):
        """
        Attach a document type to a specified workflow.
        """

        return super(
            APIWorkflowDocumentTypeList, self
        ).post(request, *args, **kwargs)


class APIWorkflowDocumentTypeView(generics.RetrieveDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'document_type_pk'
    mayan_object_permissions = {
        'GET': (permission_document_type_view,),
    }
    serializer_class = WorkflowDocumentTypeSerializer

    def delete(self, request, *args, **kwargs):
        """
        Remove a document type from the selected workflow.
        """

        return super(
            APIWorkflowDocumentTypeView, self
        ).delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected workflow document type.
        """

        return super(APIWorkflowDocumentTypeView, self).get(*args, **kwargs)

    def get_queryset(self):
        return self.get_workflow().document_types.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        """
        This view returns a document types that belongs to a workflow
        RESEARCH: Could the documents.api_views.APIDocumentTypeView class
        be subclasses for this?
        RESEARCH: Since this is a parent-child API view could this be made
        into a generic API class?
        RESEARCH: Reuse get_workflow method from APIWorkflowDocumentTypeList?
        """

        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def perform_destroy(self, instance):
        """
        RESEARCH: Move this kind of methods to the serializer instead it that
        ability becomes available in Django REST framework
        """

        self.get_workflow().document_types.remove(instance)


class APIWorkflowListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_workflow_view,),
        'POST': (permission_workflow_create,)
    }
    permission_classes = (MayanPermission,)
    queryset = Workflow.objects.all()

    def get(self, *args, **kwargs):
        """
        Returns a list of all the workflows.
        """
        return super(APIWorkflowListView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowSerializer
        else:
            return WritableWorkflowSerializer

    def post(self, *args, **kwargs):
        """
        Create a new workflow.
        """
        return super(APIWorkflowListView, self).post(*args, **kwargs)


class APIWorkflowView(generics.RetrieveUpdateDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_workflow_delete,),
        'GET': (permission_workflow_view,),
        'PATCH': (permission_workflow_edit,),
        'PUT': (permission_workflow_edit,)
    }
    queryset = Workflow.objects.all()

    def delete(self, *args, **kwargs):
        """
        Delete the selected workflow.
        """

        return super(APIWorkflowView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected workflow.
        """

        return super(APIWorkflowView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowSerializer
        else:
            return WritableWorkflowSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected workflow.
        """

        return super(APIWorkflowView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected workflow.
        """

        return super(APIWorkflowView, self).put(*args, **kwargs)


# Workflow state views


class APIWorkflowStateListView(generics.ListCreateAPIView):
    serializer_class = WorkflowStateSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the workflow states.
        """
        return super(APIWorkflowStateListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def post(self, *args, **kwargs):
        """
        Create a new workflow state.
        """
        return super(APIWorkflowStateListView, self).post(*args, **kwargs)


class APIWorkflowStateView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'state_pk'
    serializer_class = WorkflowStateSerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected workflow state.
        """

        return super(APIWorkflowStateView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected workflow state.
        """

        return super(APIWorkflowStateView, self).get(*args, **kwargs)

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def patch(self, *args, **kwargs):
        """
        Edit the selected workflow state.
        """

        return super(APIWorkflowStateView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected workflow state.
        """

        return super(APIWorkflowStateView, self).put(*args, **kwargs)


# Workflow transition views


class APIWorkflowTransitionListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns a list of all the workflow transitions.
        """
        return super(APIWorkflowTransitionListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowTransitionSerializer
        else:
            return WritableWorkflowTransitionSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def post(self, *args, **kwargs):
        """
        Create a new workflow transition.
        """
        return super(APIWorkflowTransitionListView, self).post(*args, **kwargs)


class APIWorkflowTransitionView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'transition_pk'

    def delete(self, *args, **kwargs):
        """
        Delete the selected workflow transition.
        """

        return super(APIWorkflowTransitionView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected workflow transition.
        """

        return super(APIWorkflowTransitionView, self).get(*args, **kwargs)

    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowTransitionSerializer
        else:
            return WritableWorkflowTransitionSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow': self.get_workflow(),
            'view': self
        }

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def patch(self, *args, **kwargs):
        """
        Edit the selected workflow transition.
        """

        return super(APIWorkflowTransitionView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected workflow transition.
        """

        return super(APIWorkflowTransitionView, self).put(*args, **kwargs)


# Document workflow views


class APIWorkflowInstanceListView(generics.ListAPIView):
    serializer_class = WorkflowInstanceSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the document workflows.
        """
        return super(APIWorkflowInstanceListView, self).get(*args, **kwargs)

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().workflows.all()


class APIWorkflowInstanceView(generics.RetrieveAPIView):
    lookup_url_kwarg = 'workflow_pk'
    serializer_class = WorkflowInstanceSerializer

    def get(self, *args, **kwargs):
        """
        Return the details of the selected document workflow.
        """

        return super(APIWorkflowInstanceView, self).get(*args, **kwargs)

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().workflows.all()


class APIWorkflowInstanceLogEntryListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns a list of all the document workflows log entries.
        """
        return super(APIWorkflowInstanceLogEntryListView, self).get(
            *args, **kwargs
        )

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        if self.request.method == 'GET':
            """
            Only test for permission if reading. If writing, the permission
            will be checked in the serializer

            IMPROVEMENT:
            When writing, add check for permission or ACL for the workflow.
            Failing that, check for ACLs for any of the workflow's transitions.
            Failing that, then raise PermissionDenied
            """

            AccessControlList.objects.check_access(
                permissions=permission_workflow_view, user=self.request.user,
                obj=document
            )

        return document

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowInstanceLogEntrySerializer
        else:
            return WritableWorkflowInstanceLogEntrySerializer

    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'workflow_instance': self.get_workflow_instance(),
            'view': self
        }

    def get_queryset(self):
        return self.get_workflow_instance().log_entries.all()

    def get_workflow_instance(self):
        workflow = get_object_or_404(
            self.get_document().workflows, pk=self.kwargs['workflow_pk']
        )

        return workflow

    def post(self, *args, **kwargs):
        """
        Transition a document workflow by creating a new document workflow
        log entry.
        """
        return super(
            APIWorkflowInstanceLogEntryListView, self
        ).post(*args, **kwargs)
