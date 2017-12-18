from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from documents.permissions import (
    permission_document_create, permission_document_new_version
)
from navigation import Link

from .literals import (
    SOURCE_CHOICE_WEB_FORM, SOURCE_CHOICE_EMAIL_IMAP, SOURCE_CHOICE_EMAIL_POP3,
    SOURCE_CHOICE_SANE_SCANNER, SOURCE_CHOICE_STAGING, SOURCE_CHOICE_WATCH
)
from .permissions import (
    permission_sources_setup_create, permission_sources_setup_delete,
    permission_sources_setup_edit, permission_sources_setup_view
)


def document_new_version_not_blocked(context):
    NewVersionBlock = apps.get_model(
        app_label='checkouts', model_name='NewVersionBlock'
    )

    return not NewVersionBlock.objects.is_blocked(context['object'])


link_document_create_multiple = Link(
    icon='fa fa-upload', text=_('New document'),
    view='sources:document_create_multiple'
)
link_setup_sources = Link(
    icon='fa fa-upload', permissions=(permission_sources_setup_view,),
    text=_('Sources'), view='sources:setup_source_list'
)
link_setup_source_create_imap_email = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new IMAP email'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_EMAIL_IMAP
)
link_setup_source_create_pop3_email = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new POP3 email'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_EMAIL_POP3
)
link_setup_source_create_staging_folder = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new staging folder'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_STAGING
)
link_setup_source_create_watch_folder = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new watch folder'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_WATCH
)
link_setup_source_create_webform = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new webform source'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_WEB_FORM
)
link_setup_source_create_sane_scanner = Link(
    permissions=(permission_sources_setup_create,),
    text=_('Add new SANE scanner'), view='sources:setup_source_create',
    args='"%s"' % SOURCE_CHOICE_SANE_SCANNER
)
link_setup_source_delete = Link(
    permissions=(permission_sources_setup_delete,), tags='dangerous',
    text=_('Delete'), view='sources:setup_source_delete',
    args=('resolved_object.pk',)
)
link_setup_source_edit = Link(
    text=_('Edit'), view='sources:setup_source_edit',
    args=('resolved_object.pk',), permissions=(permission_sources_setup_edit,)
)
link_source_list = Link(
    permissions=(permission_sources_setup_view,), text=_('Document sources'),
    view='sources:setup_web_form_list'
)
link_staging_file_delete = Link(
    keep_query=True,
    permissions=(permission_document_new_version, permission_document_create),
    tags='dangerous', text=_('Delete'), view='sources:staging_file_delete',
    args=('source.pk', 'object.encoded_filename',)
)
link_upload_version = Link(
    args='resolved_object.pk', condition=document_new_version_not_blocked,
    permissions=(permission_document_new_version,),
    text=_('Upload new version'), view='sources:upload_version',
)
link_setup_source_logs = Link(
    text=_('Logs'), view='sources:setup_source_logs',
    args=('resolved_object.pk',), permissions=(permission_sources_setup_view,)
)
link_setup_source_check_now = Link(
    text=_('Check now'), view='sources:setup_source_check',
    args=('resolved_object.pk',), permissions=(permission_sources_setup_view,)
)
