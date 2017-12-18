from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, resolve_url
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import parse_qs, urlparse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from acls.models import AccessControlList
from common.generics import SimpleView, SingleObjectListView
from common.utils import resolve
from converter.literals import DEFAULT_ROTATION, DEFAULT_ZOOM_LEVEL

from ..forms import DocumentPageForm
from ..models import Document, DocumentPage
from ..permissions import permission_document_view
from ..settings import (
    setting_rotation_step, setting_zoom_percent_step, setting_zoom_max_level,
    setting_zoom_min_level
)

logger = logging.getLogger(__name__)


class DocumentPageListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=self.get_document()
        )

        return super(
            DocumentPageListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'list_as_items': True,
            'object': self.get_document(),
            'title': _('Pages for document: %s') % self.get_document(),
        }

    def get_object_list(self):
        return self.get_document().pages.all()


class DocumentPageNavigationBase(RedirectView):
    def dispatch(self, request, *args, **kwargs):
        document_page = self.get_object()

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=document_page.document
        )

        return super(DocumentPageNavigationBase, self).dispatch(
            request, *args, **kwargs
        )

    def get_object(self):
        return get_object_or_404(DocumentPage, pk=self.kwargs['pk'])

    def get_redirect_url(self, *args, **kwargs):
        parse_result = urlparse(
            self.request.META.get(
                'HTTP_REFERER', resolve_url(
                    settings.LOGIN_REDIRECT_URL
                )
            )
        )

        query_dict = parse_qs(parse_result.query)

        resolver_match = resolve(parse_result.path)

        # Default is to stay on the same view
        url = parse_result.path, query_dict

        new_object = self.navigation_function()

        # Inject new_object pk in the referer's view pk or object_id kwargs
        if 'pk' in resolver_match.kwargs:
            resolver_match.kwargs['pk'] = new_object.pk
            url = reverse(
                resolver_match.view_name, kwargs=resolver_match.kwargs
            )
        elif 'object_id' in resolver_match.kwargs:
            resolver_match.kwargs['object_id'] = new_object.pk
            url = reverse(
                resolver_match.view_name, kwargs=resolver_match.kwargs
            )
        else:
            messages.warning(
                self.request, _(
                    'Unknown view keyword argument schema, unable to '
                    'redirect.'
                )
            )

        return '{}?{}'.format(url, urlencode(query_dict, doseq=True))


class DocumentPageNavigationFirst(DocumentPageNavigationBase):
    def navigation_function(self):
        document_page = self.get_object()

        return document_page.siblings.first()


class DocumentPageNavigationLast(DocumentPageNavigationBase):
    def navigation_function(self):
        document_page = self.get_object()

        return document_page.siblings.last()


class DocumentPageNavigationNext(DocumentPageNavigationBase):
    def navigation_function(self):
        document_page = self.get_object()

        try:
            document_page = document_page.siblings.get(
                page_number=document_page.page_number + 1
            )
        except DocumentPage.DoesNotExist:
            messages.warning(
                self.request, _('There are no more pages in this document')
            )
        finally:
            return document_page


class DocumentPageNavigationPrevious(DocumentPageNavigationBase):
    def navigation_function(self):
        document_page = self.get_object()

        try:
            document_page = document_page.siblings.get(
                page_number=document_page.page_number - 1
            )
        except DocumentPage.DoesNotExist:
            messages.warning(
                self.request, _(
                    'You are already at the first page of this document'
                )
            )
        finally:
            return document_page


class DocumentPageView(SimpleView):
    template_name = 'appearance/generic_form.html'

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=self.get_object().document
        )

        return super(
            DocumentPageView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        zoom = int(self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL))
        rotation = int(self.request.GET.get('rotation', DEFAULT_ROTATION))

        document_page_form = DocumentPageForm(
            instance=self.get_object(), zoom=zoom, rotation=rotation
        )

        base_title = _('Image of: %s') % self.get_object()

        if zoom != DEFAULT_ZOOM_LEVEL:
            zoom_text = '({}%)'.format(zoom)
        else:
            zoom_text = ''

        return {
            'form': document_page_form,
            'hide_labels': True,
            'navigation_object_list': ('page',),
            'page': self.get_object(),
            'rotation': rotation,
            'title': ' '.join((base_title, zoom_text,)),
            'read_only': True,
            'zoom': zoom,
        }

    def get_object(self):
        return get_object_or_404(DocumentPage, pk=self.kwargs['pk'])


class DocumentPageViewResetView(RedirectView):
    pattern_name = 'documents:document_page_view'


class DocumentPageInteractiveTransformation(RedirectView):
    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=object
        )

        return super(DocumentPageInteractiveTransformation, self).dispatch(
            request, *args, **kwargs
        )

    def get_object(self):
        return get_object_or_404(DocumentPage, pk=self.kwargs['pk'])

    def get_redirect_url(self, *args, **kwargs):
        url = reverse(
            'documents:document_page_view', args=(self.kwargs['pk'],)
        )

        query_dict = {
            'rotation': int(
                self.request.GET.get('rotation', DEFAULT_ROTATION)
            ), 'zoom': int(self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL))
        }

        self.transformation_function(query_dict)

        return '{}?{}'.format(url, urlencode(query_dict))


class DocumentPageZoomInView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = query_dict['zoom'] + setting_zoom_percent_step.value

        if zoom > setting_zoom_max_level.value:
            zoom = setting_zoom_max_level.value

        query_dict['zoom'] = zoom


class DocumentPageZoomOutView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = query_dict['zoom'] - setting_zoom_percent_step.value

        if zoom < setting_zoom_min_level.value:
            zoom = setting_zoom_min_level.value

        query_dict['zoom'] = zoom


class DocumentPageRotateLeftView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            query_dict['rotation'] - setting_rotation_step.value
        ) % 360


class DocumentPageRotateRightView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            query_dict['rotation'] + setting_rotation_step.value
        ) % 360
