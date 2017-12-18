from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.core.files.base import ContentFile
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from common.generics import (
    ConfirmView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectDetailView, SingleObjectDownloadView, SingleObjectListView,
    SimpleView
)

from .forms import KeyDetailForm, KeySearchForm
from .literals import KEY_TYPE_PUBLIC
from .models import Key
from .permissions import (
    permission_key_delete, permission_key_download, permission_key_receive,
    permission_key_upload, permission_key_view, permission_keyserver_query
)

logger = logging.getLogger(__name__)


class KeyDeleteView(SingleObjectDeleteView):
    model = Key
    object_permission = permission_key_delete

    def get_post_action_redirect(self):
        if self.get_object().key_type == KEY_TYPE_PUBLIC:
            return reverse_lazy('django_gpg:key_public_list')
        else:
            return reverse_lazy('django_gpg:key_private_list')

    def get_extra_context(self):
        return {'title': _('Delete key: %s') % self.get_object()}


class KeyDetailView(SingleObjectDetailView):
    form_class = KeyDetailForm
    model = Key
    object_permission = permission_key_view

    def get_extra_context(self):
        return {
            'title': _('Details for key: %s') % self.get_object(),
        }


class KeyDownloadView(SingleObjectDownloadView):
    model = Key
    object_permission = permission_key_download

    def get_file(self):
        key = self.get_object()

        return ContentFile(key.key_data, name=key.key_id)


class KeyReceive(ConfirmView):
    post_action_redirect = reverse_lazy('django_gpg:key_public_list')
    view_permission = permission_key_receive

    def get_extra_context(self):
        return {
            'message': _('Import key ID: %s?') % self.kwargs['key_id'],
            'title': _('Import key'),
        }

    def view_action(self):
        try:
            Key.objects.receive_key(key_id=self.kwargs['key_id'])
        except Exception as exception:
            messages.error(
                self.request,
                _('Unable to import key: %(key_id)s; %(error)s') % {
                    'key_id': self.kwargs['key_id'],
                    'error': exception,
                }
            )
        else:
            messages.success(
                self.request, _('Successfully received key: %(key_id)s') % {
                    'key_id': self.kwargs['key_id'],
                }
            )


class KeyQueryView(SimpleView):
    template_name = 'appearance/generic_form.html'
    view_permission = permission_keyserver_query

    def get_form(self):
        if ('term' in self.request.GET) and self.request.GET['term'].strip():
            term = self.request.GET['term']
            return KeySearchForm(initial={'term': term})
        else:
            return KeySearchForm()

    def get_extra_context(self):
        return {
            'form': self.get_form(),
            'form_action': reverse('django_gpg:key_query_results'),
            'submit_icon': 'fa fa-search',
            'submit_label': _('Search'),
            'submit_method': 'GET',
            'title': _('Query key server'),
        }


class KeyQueryResultView(SingleObjectListView):
    view_permission = permission_keyserver_query

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Key query results'),
        }

    def get_object_list(self):
        term = self.request.GET.get('term')
        if term:
            return Key.objects.search(query=term)
        else:
            return ()


class KeyUploadView(SingleObjectCreateView):
    fields = ('key_data',)
    model = Key
    post_action_redirect = reverse_lazy('django_gpg:key_public_list')
    view_permission = permission_key_upload

    def get_extra_context(self):
        return {
            'title': _('Upload new key'),
        }


class PublicKeyListView(SingleObjectListView):
    object_permission = permission_key_view
    queryset = Key.objects.public_keys()

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Public keys')
        }


class PrivateKeyListView(SingleObjectListView):
    object_permission = permission_key_view
    queryset = Key.objects.private_keys()

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Private keys')
        }
