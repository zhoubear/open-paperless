from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from .literals import SOURCE_UNCOMPRESS_CHOICE_ASK


def create_default_document_source(sender, **kwargs):
    WebFormSource = apps.get_model(
        app_label='sources', model_name='WebFormSource'
    )

    if not WebFormSource.objects.count():
        WebFormSource.objects.create(
            label=_('Default'), uncompress=SOURCE_UNCOMPRESS_CHOICE_ASK
        )


def copy_transformations_to_version(sender, **kwargs):
    Transformation = apps.get_model(
        app_label='converter', model_name='Transformation'
    )

    instance = kwargs['instance']

    # TODO: Fix this, source should be previous version
    # TODO: Fix this, shouldn't this be at the documents app
    Transformation.objects.copy(
        source=instance.document, targets=instance.pages.all()
    )


def initialize_periodic_tasks(sender, **kwargs):
    POP3Email = apps.get_model(app_label='sources', model_name='POP3Email')
    IMAPEmail = apps.get_model(app_label='sources', model_name='IMAPEmail')
    WatchFolderSource = apps.get_model(
        app_label='sources', model_name='WatchFolderSource'
    )

    for source in POP3Email.objects.filter(enabled=True):
        source.save()

    for source in IMAPEmail.objects.filter(enabled=True):
        source.save()

    for source in WatchFolderSource.objects.filter(enabled=True):
        source.save()
