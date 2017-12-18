from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from converter.permissions import (
    permission_transformation_delete, permission_transformation_edit
)
from navigation import Link

from .permissions import (
    permission_document_delete, permission_document_download,
    permission_document_properties_edit, permission_document_print,
    permission_document_restore, permission_document_tools,
    permission_document_version_revert, permission_document_view,
    permission_document_trash, permission_document_type_create,
    permission_document_type_delete, permission_document_type_edit,
    permission_document_type_view, permission_empty_trash,
    permission_document_version_view
)
from .settings import setting_zoom_max_level, setting_zoom_min_level


def is_not_current_version(context):
    # Use the 'object' key when the document version is an object in a list,
    # such as when showing the version list view and use the 'resolved_object'
    # when the document version is the context object, such as when showing the
    # signatures list of a documern version. This can be fixed by updating
    # the navigations app object resolution logic to use 'resolved_object' even
    # for objects in a list.
    document_version = context.get('object', context['resolved_object'])
    return document_version.document.latest_version.timestamp != document_version.timestamp


def is_first_page(context):
    return context['resolved_object'].page_number <= 1


def is_last_page(context):
    return context['resolved_object'].page_number >= context['resolved_object'].document_version.pages.count()


def is_max_zoom(context):
    return context['zoom'] >= setting_zoom_max_level.value


def is_min_zoom(context):
    return context['zoom'] <= setting_zoom_min_level.value


# Facet
link_document_preview = Link(
    icon='fa fa-eye', permissions=(permission_document_view,),
    text=_('Preview'), view='documents:document_preview',
    args='resolved_object.id'
)
link_document_properties = Link(
    icon='fa fa-info', permissions=(permission_document_view,),
    text=_('Properties'), view='documents:document_properties',
    args='resolved_object.id'
)
link_document_version_list = Link(
    icon='fa fa-code-fork', permissions=(permission_document_version_view,),
    text=_('Versions'), view='documents:document_version_list',
    args='resolved_object.pk'
)
link_document_pages = Link(
    icon='fa fa-files-o', permissions=(permission_document_view,),
    text=_('Pages'), view='documents:document_pages', args='resolved_object.pk'
)

# Actions
link_document_clear_transformations = Link(
    permissions=(permission_transformation_delete,),
    text=_('Clear transformations'),
    view='documents:document_clear_transformations', args='resolved_object.id'
)
link_document_clone_transformations = Link(
    permissions=(permission_transformation_edit,),
    text=_('Clone transformations'),
    view='documents:document_clone_transformations', args='resolved_object.id'
)
link_document_delete = Link(
    permissions=(permission_document_delete,), tags='dangerous',
    text=_('Delete'), view='documents:document_delete',
    args='resolved_object.id'
)
link_document_trash = Link(
    permissions=(permission_document_trash,), tags='dangerous',
    text=_('Move to trash'), view='documents:document_trash',
    args='resolved_object.id'
)
link_document_edit = Link(
    permissions=(permission_document_properties_edit,),
    text=_('Edit properties'), view='documents:document_edit',
    args='resolved_object.id'
)
link_document_document_type_edit = Link(
    permissions=(permission_document_properties_edit,), text=_('Change type'),
    view='documents:document_document_type_edit', args='resolved_object.id'
)
link_document_download = Link(
    permissions=(permission_document_download,), text=_('Download'),
    view='documents:document_download_form', args='resolved_object.id'
)
link_document_print = Link(
    permissions=(permission_document_print,), text=_('Print'),
    view='documents:document_print', args='resolved_object.id'
)
link_document_update_page_count = Link(
    args='resolved_object.pk', permissions=(permission_document_tools,),
    text=_('Recalculate page count'),
    view='documents:document_update_page_count'
)
link_document_restore = Link(
    permissions=(permission_document_restore,), text=_('Restore'),
    view='documents:document_restore', args='object.pk'
)
link_document_multiple_clear_transformations = Link(
    permissions=(permission_transformation_delete,),
    text=_('Clear transformations'),
    view='documents:document_multiple_clear_transformations'
)
link_document_multiple_trash = Link(
    tags='dangerous', text=_('Move to trash'),
    view='documents:document_multiple_trash'
)
link_document_multiple_delete = Link(
    tags='dangerous', text=_('Delete'),
    view='documents:document_multiple_delete'
)
link_document_multiple_document_type_edit = Link(
    text=_('Change type'),
    view='documents:document_multiple_document_type_edit'
)
link_document_multiple_download = Link(
    text=_('Download'), view='documents:document_multiple_download_form'
)
link_document_multiple_update_page_count = Link(
    text=_('Recalculate page count'),
    view='documents:document_multiple_update_page_count'
)
link_document_multiple_restore = Link(
    text=_('Restore'), view='documents:document_multiple_restore'
)

# Versions
link_document_version_download = Link(
    args='resolved_object.pk', permissions=(permission_document_download,),
    text=_('Download version'), view='documents:document_version_download_form'
)
link_document_version_return_document = Link(
    icon='fa fa-file', permissions=(permission_document_view,),
    text=_('Document'), view='documents:document_preview',
    args='resolved_object.document.pk'
)
link_document_version_return_list = Link(
    icon='fa fa-code-fork', permissions=(permission_document_version_view,),
    text=_('Versions'), view='documents:document_version_list',
    args='resolved_object.document.pk'
)
link_document_version_view = Link(
    args='resolved_object.pk', permissions=(permission_document_version_view,),
    text=_('Details'), view='documents:document_version_view'
)

# Views
link_document_list = Link(
    icon='fa fa-file', text=_('All documents'), view='documents:document_list'
)
link_document_list_recent = Link(
    icon='fa fa-clock-o', text=_('Recent documents'),
    view='documents:document_list_recent'
)
link_document_list_deleted = Link(
    icon='fa fa-trash', text=_('Trash can'),
    view='documents:document_list_deleted'
)

# Tools
link_clear_image_cache = Link(
    icon='fa fa-file-image-o',
    description=_(
        'Clear the graphics representations used to speed up the documents\' '
        'display and interactive transformations results.'
    ), permissions=(permission_document_tools,),
    text=_('Clear document image cache'),
    view='documents:document_clear_image_cache'
)
link_trash_can_empty = Link(
    permissions=(permission_empty_trash,), text=_('Empty trash'),
    view='documents:trash_can_empty'
)

# Document pages
link_document_page_navigation_first = Link(
    conditional_disable=is_first_page, icon='fa fa-step-backward',
    keep_query=True, permissions=(permission_document_view,),
    text=_('First page'), view='documents:document_page_navigation_first',
    args='resolved_object.pk'
)
link_document_page_navigation_last = Link(
    conditional_disable=is_last_page, icon='fa fa-step-forward',
    keep_query=True, text=_('Last page'),
    permissions=(permission_document_view,),
    view='documents:document_page_navigation_last', args='resolved_object.pk'
)
link_document_page_navigation_previous = Link(
    conditional_disable=is_first_page, icon='fa fa-arrow-left',
    keep_query=True, permissions=(permission_document_view,),
    text=_('Previous page'),
    view='documents:document_page_navigation_previous',
    args='resolved_object.pk'
)
link_document_page_navigation_next = Link(
    conditional_disable=is_last_page, icon='fa fa-arrow-right',
    keep_query=True, text=_('Next page'),
    permissions=(permission_document_view,),
    view='documents:document_page_navigation_next', args='resolved_object.pk'
)
link_document_page_return = Link(
    icon='fa fa-file', permissions=(permission_document_view,),
    text=_('Document'), view='documents:document_preview',
    args='resolved_object.document.pk'
)
link_document_page_rotate_left = Link(
    icon='fa fa-rotate-left', permissions=(permission_document_view,),
    text=_('Rotate left'), view='documents:document_page_rotate_left',
    args='resolved_object.pk', keep_query=True
)
link_document_page_rotate_right = Link(
    icon='fa fa-rotate-right', permissions=(permission_document_view,),
    text=_('Rotate right'), view='documents:document_page_rotate_right',
    args='resolved_object.pk', keep_query=True
)
link_document_page_view = Link(
    permissions=(permission_document_view,), text=_('Page image'),
    view='documents:document_page_view', args='resolved_object.pk'
)
link_document_page_view_reset = Link(
    permissions=(permission_document_view,), text=_('Reset view'),
    view='documents:document_page_view_reset', args='resolved_object.pk'
)
link_document_page_zoom_in = Link(
    conditional_disable=is_max_zoom, icon='fa fa-search-plus',
    permissions=(permission_document_view,), text=_('Zoom in'),
    view='documents:document_page_zoom_in', args='resolved_object.pk',
    keep_query=True
)
link_document_page_zoom_out = Link(
    conditional_disable=is_min_zoom, icon='fa fa-search-minus',
    permissions=(permission_document_view,), text=_('Zoom out'),
    view='documents:document_page_zoom_out', args='resolved_object.pk',
    keep_query=True
)

# Document versions
link_document_version_revert = Link(
    condition=is_not_current_version,
    permissions=(permission_document_version_revert,), tags='dangerous',
    text=_('Revert'), view='documents:document_version_revert',
    args='object.pk'
)

# Document type related links
link_document_type_create = Link(
    permissions=(permission_document_type_create,),
    text=_('Create document type'), view='documents:document_type_create'
)
link_document_type_delete = Link(
    permissions=(permission_document_type_delete,), tags='dangerous',
    text=_('Delete'), view='documents:document_type_delete',
    args='resolved_object.id'
)
link_document_type_edit = Link(
    permissions=(permission_document_type_edit,), text=_('Edit'),
    view='documents:document_type_edit', args='resolved_object.id'
)
link_document_type_filename_create = Link(
    permissions=(permission_document_type_edit,),
    text=_('Add quick label to document type'),
    view='documents:document_type_filename_create', args='document_type.id'
)
link_document_type_filename_delete = Link(
    permissions=(permission_document_type_edit,), tags='dangerous',
    text=_('Delete'), view='documents:document_type_filename_delete',
    args='resolved_object.id'
)
link_document_type_filename_edit = Link(
    permissions=(permission_document_type_edit,), text=_('Edit'),
    view='documents:document_type_filename_edit', args='resolved_object.id'
)
link_document_type_filename_list = Link(
    permissions=(permission_document_type_view,), text=_('Quick labels'),
    view='documents:document_type_filename_list', args='resolved_object.id'
)
link_document_type_list = Link(
    permissions=(permission_document_type_view,), text=_('Document types'),
    view='documents:document_type_list'
)
link_document_type_setup = Link(
    icon='fa fa-file', permissions=(permission_document_type_view,),
    text=_('Document types'), view='documents:document_type_list'
)
link_duplicated_document_list = Link(
    icon='fa fa-clone', text=_('Duplicated documents'),
    view='documents:duplicated_document_list'
)
link_document_duplicates_list = Link(
    args='resolved_object.id', icon='fa fa-clone',
    permissions=(permission_document_view,), text=_('Duplicates'),
    view='documents:document_duplicates_list',
)
link_duplicated_document_scan = Link(
    icon='fa fa-clone', text=_('Duplicated document scan'),
    view='documents:duplicated_document_scan'
)
