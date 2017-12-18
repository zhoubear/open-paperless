from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from checkouts.models import NewVersionBlock
from common import menu_facet
from common.models import SharedUploadedFile
from common.utils import encapsulate
from common.views import (
    ConfirmView, MultiFormView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectEditView, SingleObjectListView
)
from common.widgets import two_state_template
from documents.models import DocumentType, Document
from documents.permissions import (
    permission_document_create, permission_document_new_version
)
from documents.tasks import task_upload_new_version
from metadata.api import decode_metadata_from_url
from navigation import Link

from .exceptions import SourceException
from .forms import (
    NewDocumentForm, NewVersionForm, WebFormUploadForm, WebFormUploadFormHTML5
)
from .literals import SOURCE_UNCOMPRESS_CHOICE_ASK, SOURCE_UNCOMPRESS_CHOICE_Y
from .models import (
    InteractiveSource, Source, SaneScanner, StagingFolderSource
)
from .permissions import (
    permission_sources_setup_create, permission_sources_setup_delete,
    permission_sources_setup_edit, permission_sources_setup_view,
    permission_staging_file_delete
)
from .tasks import task_check_interval_source, task_source_handle_upload
from .utils import get_class, get_form_class, get_upload_form_class


class SourceLogListView(SingleObjectListView):
    view_permission = permission_sources_setup_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_source(),
            'title': _('Log entries for source: %s') % self.get_source(),
        }

    def get_object_list(self):
        return self.get_source().logs.all()

    def get_source(self):
        return get_object_or_404(
            Source.objects.select_subclasses(), pk=self.kwargs['pk']
        )


class UploadBaseView(MultiFormView):
    template_name = 'appearance/generic_form.html'
    prefixes = {'source_form': 'source', 'document_form': 'document'}

    @staticmethod
    def get_tab_link_for_source(source, document=None):
        if document:
            view = 'sources:upload_version'
            args = ('"{}"'.format(document.pk), '"{}"'.format(source.pk),)
        else:
            view = 'sources:upload_interactive'
            args = ('"{}"'.format(source.pk),)

        return Link(
            text=source.label,
            view=view,
            args=args,
            keep_query=True,
            remove_from_query=['page'],
            icon='fa fa-upload',
        )

    @staticmethod
    def get_active_tab_links(document=None):
        return [
            UploadBaseView.get_tab_link_for_source(source, document)
            for source in InteractiveSource.objects.filter(enabled=True).select_subclasses()
        ]

    def dispatch(self, request, *args, **kwargs):
        if 'source_id' in kwargs:
            self.source = get_object_or_404(
                Source.objects.filter(enabled=True).select_subclasses(),
                pk=kwargs['source_id']
            )
        else:
            self.source = InteractiveSource.objects.filter(
                enabled=True
            ).select_subclasses().first()

        if not InteractiveSource.objects.filter(enabled=True).exists():
            messages.error(
                request,
                _(
                    'No interactive document sources have been defined or '
                    'none have been enabled, create one before proceeding.'
                )
            )
            return HttpResponseRedirect(reverse('sources:setup_source_list'))

        return super(UploadBaseView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadBaseView, self).get_context_data(**kwargs)
        subtemplates_list = []

        context['source'] = self.source

        if isinstance(self.source, StagingFolderSource):
            try:
                staging_filelist = list(self.source.get_files())
            except Exception as exception:
                messages.error(self.request, exception)
                staging_filelist = []
            finally:
                subtemplates_list = [
                    {
                        'name': 'appearance/generic_multiform_subtemplate.html',
                        'context': {
                            'forms': context['forms'],
                            'title': _('Document properties'),
                        }
                    },
                    {
                        'name': 'appearance/generic_list_subtemplate.html',
                        'context': {
                            'hide_link': True,
                            'object_list': staging_filelist,
                            'title': _('Files in staging path'),
                        }
                    },
                ]
        elif isinstance(self.source, SaneScanner):
            subtemplates_list.append({
                'name': 'sources/upload_multiform_subtemplate.html',
                'context': {
                    'forms': context['forms'],
                    'is_multipart': True,
                    'title': _('Document properties'),
                    'submit_label': _('Scan'),
                },
            })
        else:
            subtemplates_list.append({
                'name': 'sources/upload_multiform_subtemplate.html',
                'context': {
                    'forms': context['forms'],
                    'is_multipart': True,
                    'title': _('Document properties'),
                },
            })

        menu_facet.bound_links['sources:upload_interactive'] = self.tab_links
        menu_facet.bound_links['sources:upload_version'] = self.tab_links

        context.update({
            'subtemplates_list': subtemplates_list,
        })

        return context


class UploadInteractiveView(UploadBaseView):
    def dispatch(self, request, *args, **kwargs):
        self.subtemplates_list = []

        self.document_type = get_object_or_404(
            DocumentType,
            pk=self.request.GET.get(
                'document_type_id', self.request.POST.get('document_type_id')
            )
        )

        AccessControlList.objects.check_access(
            permissions=permission_document_create, user=request.user,
            obj=self.document_type
        )

        self.tab_links = UploadBaseView.get_active_tab_links()

        try:
            return super(
                UploadInteractiveView, self
            ).dispatch(request, *args, **kwargs)
        except Exception as exception:
            if request.is_ajax():
                return JsonResponse(
                    data={'error': force_text(exception)}, status=500
                )
            else:
                raise

    def forms_valid(self, forms):
        if self.source.can_compress:
            if self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_ASK:
                expand = forms['source_form'].cleaned_data.get('expand')
            else:
                if self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_Y:
                    expand = True
                else:
                    expand = False
        else:
            expand = False

        try:
            uploaded_file = self.source.get_upload_file_object(
                forms['source_form'].cleaned_data
            )
        except SourceException as exception:
            messages.error(self.request, exception)
        else:
            shared_uploaded_file = SharedUploadedFile.objects.create(
                file=uploaded_file.file
            )

            label = None

            if 'document_type_available_filenames' in forms['document_form'].cleaned_data:
                if forms['document_form'].cleaned_data['document_type_available_filenames']:
                    label = forms['document_form'].cleaned_data['document_type_available_filenames'].filename

            if not self.request.user.is_anonymous:
                user_id = self.request.user.pk
            else:
                user_id = None

            try:
                self.source.clean_up_upload_file(uploaded_file)
            except Exception as exception:
                messages.error(self.request, exception)

            task_source_handle_upload.apply_async(kwargs=dict(
                description=forms['document_form'].cleaned_data.get('description'),
                document_type_id=self.document_type.pk,
                expand=expand,
                label=label,
                language=forms['document_form'].cleaned_data.get('language'),
                metadata_dict_list=decode_metadata_from_url(self.request.GET),
                shared_uploaded_file_id=shared_uploaded_file.pk,
                source_id=self.source.pk,
                tag_ids=self.request.GET.getlist('tags'),
                user_id=user_id,
            ))
            messages.success(
                self.request,
                _(
                    'New document queued for uploaded and will be available '
                    'shortly.'
                )
            )

        return HttpResponseRedirect(
            '{}?{}'.format(
                reverse(self.request.resolver_match.view_name),
                self.request.META['QUERY_STRING']
            ),
        )

    def create_source_form_form(self, **kwargs):
        if hasattr(self.source, 'uncompress'):
            show_expand = self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_ASK
        else:
            show_expand = False

        return self.get_form_classes()['source_form'](
            prefix=kwargs['prefix'],
            source=self.source,
            show_expand=show_expand,
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def create_document_form_form(self, **kwargs):
        return self.get_form_classes()['document_form'](
            prefix=kwargs['prefix'],
            document_type=self.document_type,
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def get_form_classes(self):
        source_form_class = get_upload_form_class(self.source.source_type)

        # Override source form class to enable the HTML5 file uploader
        if source_form_class == WebFormUploadForm:
            source_form_class = WebFormUploadFormHTML5

        return {
            'document_form': NewDocumentForm,
            'source_form': source_form_class
        }

    def get_context_data(self, **kwargs):
        context = super(UploadInteractiveView, self).get_context_data(**kwargs)
        context['title'] = _(
            'Upload a local document from source: %s'
        ) % self.source.label
        if not isinstance(self.source, StagingFolderSource) and not isinstance(self.source, SaneScanner):
            context['subtemplates_list'][0]['context'].update(
                {
                    'form_action': '{}?{}'.format(
                        reverse(self.request.resolver_match.view_name),
                        self.request.META['QUERY_STRING']
                    ),
                    'form_class': 'dropzone',
                    'form_disable_submit': True,
                    'form_id': 'html5upload',
                }
            )
        return context


class UploadInteractiveVersionView(UploadBaseView):
    def dispatch(self, request, *args, **kwargs):

        self.subtemplates_list = []

        self.document = get_object_or_404(Document, pk=kwargs['document_pk'])

        # TODO: Try to remove this new version block check from here
        if NewVersionBlock.objects.is_blocked(self.document):
            messages.error(
                self.request,
                _(
                    'Document "%s" is blocked from uploading new versions.'
                ) % self.document
            )
            return HttpResponseRedirect(
                reverse(
                    'documents:document_version_list', args=(self.document.pk,)
                )
            )

        AccessControlList.objects.check_access(
            permissions=permission_document_new_version,
            user=self.request.user, obj=self.document
        )

        self.tab_links = UploadBaseView.get_active_tab_links(self.document)

        return super(
            UploadInteractiveVersionView, self
        ).dispatch(request, *args, **kwargs)

    def forms_valid(self, forms):
        try:
            uploaded_file = self.source.get_upload_file_object(
                forms['source_form'].cleaned_data
            )
        except SourceException as exception:
            messages.error(self.request, exception)
        else:
            shared_uploaded_file = SharedUploadedFile.objects.create(
                file=uploaded_file.file
            )

            try:
                self.source.clean_up_upload_file(uploaded_file)
            except Exception as exception:
                messages.error(self.request, exception)

            if not self.request.user.is_anonymous:
                user_id = self.request.user.pk
            else:
                user_id = None

            task_upload_new_version.apply_async(kwargs=dict(
                shared_uploaded_file_id=shared_uploaded_file.pk,
                document_id=self.document.pk,
                user_id=user_id,
                comment=forms['document_form'].cleaned_data.get('comment')
            ))

            messages.success(
                self.request,
                _(
                    'New document version queued for uploaded and will be '
                    'available shortly.'
                )
            )

        return HttpResponseRedirect(
            reverse(
                'documents:document_version_list', args=(self.document.pk,)
            )
        )

    def create_source_form_form(self, **kwargs):
        return self.get_form_classes()['source_form'](
            prefix=kwargs['prefix'],
            source=self.source,
            show_expand=False,
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def create_document_form_form(self, **kwargs):
        return self.get_form_classes()['document_form'](
            prefix=kwargs['prefix'],
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def get_form_classes(self):
        return {
            'document_form': NewVersionForm,
            'source_form': get_upload_form_class(self.source.source_type)
        }

    def get_context_data(self, **kwargs):
        context = super(
            UploadInteractiveVersionView, self
        ).get_context_data(**kwargs)
        context['object'] = self.document
        context['title'] = _(
            'Upload a new version from source: %s'
        ) % self.source.label

        return context


class StagingFileDeleteView(SingleObjectDeleteView):
    object_permission = permission_staging_file_delete
    object_permission_related = 'staging_folder'

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'object_name': _('Staging file'),
            'source': self.get_source(),
        }

    def get_object(self):
        source = self.get_source()
        return source.get_file(
            encoded_filename=self.kwargs['encoded_filename']
        )

    def get_source(self):
        return get_object_or_404(
            StagingFolderSource, pk=self.kwargs['pk']
        )


# Setup views
class SetupSourceCheckView(ConfirmView):
    """
    Trigger the task_check_interval_source task for a given source to
    test/debug their configuration irrespective of the schedule task setup.
    """
    view_permission = permission_sources_setup_view

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Trigger check for source "%s"?') % self.get_object(),
        }

    def get_object(self):
        return get_object_or_404(Source.objects.select_subclasses(), pk=self.kwargs['pk'])

    def view_action(self):
        task_check_interval_source.apply_async(
            kwargs={
                'source_id': self.get_object().pk
            }
        )

        messages.success(self.request, _('Source check queued.'))


class SetupSourceCreateView(SingleObjectCreateView):
    post_action_redirect = reverse_lazy('sources:setup_source_list')
    view_permission = permission_sources_setup_create

    def get_form_class(self):
        return get_form_class(self.kwargs['source_type'])

    def get_extra_context(self):
        return {
            'object': self.kwargs['source_type'],
            'title': _(
                'Create new source of type: %s'
            ) % get_class(self.kwargs['source_type']).class_fullname(),
        }


class SetupSourceDeleteView(SingleObjectDeleteView):
    post_action_redirect = reverse_lazy('sources:setup_source_list')
    view_permission = permission_sources_setup_delete

    def get_object(self):
        return get_object_or_404(
            Source.objects.select_subclasses(), pk=self.kwargs['pk']
        )

    def get_form_class(self):
        return get_form_class(self.get_object().source_type)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the source: %s?') % self.get_object(),
        }


class SetupSourceEditView(SingleObjectEditView):
    post_action_redirect = reverse_lazy('sources:setup_source_list')
    view_permission = permission_sources_setup_edit

    def get_object(self):
        return get_object_or_404(
            Source.objects.select_subclasses(), pk=self.kwargs['pk']
        )

    def get_form_class(self):
        return get_form_class(self.get_object().source_type)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit source: %s') % self.get_object(),
        }


class SetupSourceListView(SingleObjectListView):
    extra_context = {
        'extra_columns': (
            {
                'name': _('Type'),
                'attribute': encapsulate(lambda entry: entry.class_fullname())
            },
            {
                'name': _('Enabled'),
                'attribute': encapsulate(
                    lambda entry: two_state_template(entry.enabled)
                )
            },
        ),
        'hide_link': True,
        'title': _('Sources'),
    }
    queryset = Source.objects.select_subclasses()
    view_permission = permission_sources_setup_view
