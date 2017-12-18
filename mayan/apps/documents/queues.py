from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from common.queues import queue_tools
from task_manager.classes import CeleryQueue

queue_converter = CeleryQueue(
    name='converter', label=_('Converter'), transient=True
)
queue_documents_periodic = CeleryQueue(
    name='documents_periodic', label=_('Documents periodic'), transient=True
)
queue_uploads = CeleryQueue(
    name='uploads', label=_('Uploads')
)
queue_uploads = CeleryQueue(
    name='documents', label=_('Documents')
)

queue_documents_periodic.add_task_type(
    name='documents.tasks.task_check_delete_periods',
    label=_('Check document type delete periods')
)
queue_documents_periodic.add_task_type(
    name='documents.tasks.task_check_trash_periods',
    label=_('Check document type trash periods')
)
queue_documents_periodic.add_task_type(
    name='documents.tasks.task_delete_stubs',
    label=_('Delete document stubs')
)

queue_tools.add_task_type(
    name='documents.tasks.task_clear_image_cache',
    label=_('Clear image cache')
)

queue_converter.add_task_type(
    name='documents.tasks.task_generate_document_page_image',
    label=_('Generate document page image')
)

queue_uploads.add_task_type(
    name='documents.tasks.task_update_page_count',
    label=_('Update document page count')
)
queue_uploads.add_task_type(
    name='documents.tasks.task_upload_new_version',
    label=_('Upload new document version')
)
queue_uploads.add_task_type(
    name='documents.tasks.task_delete_document',
    label=_('Delete a document')
)
