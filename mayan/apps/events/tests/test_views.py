from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType

from documents.tests.test_views import GenericDocumentViewTestCase

from ..permissions import permission_events_view


class EventsViewTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(EventsViewTestCase, self).setUp()

        content_type = ContentType.objects.get_for_model(self.document)

        self.view_arguments = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': self.document.pk
        }

    def test_events_for_object_view_no_permission(self):
        self.login_user()

        document = self.document.add_as_recent_document_for_user(
            self.user
        ).document

        content_type = ContentType.objects.get_for_model(document)

        view_arguments = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': document.pk
        }

        response = self.get(
            viewname='events:events_for_object', kwargs=view_arguments
        )

        self.assertNotContains(response, text=document.label, status_code=403)
        self.assertNotContains(response, text='otal:', status_code=403)

    def test_events_for_object_view_with_permission(self):
        self.login_user()

        self.role.permissions.add(
            permission_events_view.stored_permission
        )

        document = self.document.add_as_recent_document_for_user(
            self.user
        ).document

        content_type = ContentType.objects.get_for_model(document)

        view_arguments = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': document.pk
        }

        response = self.get(
            viewname='events:events_for_object', kwargs=view_arguments
        )

        self.assertContains(response, text=document.label, status_code=200)
        self.assertNotContains(response, text='otal: 0', status_code=200)
