from __future__ import unicode_literals

import logging

from django.apps import apps

from mayan.celery import app

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_launch_all_workflows():
    Document = apps.get_model(app_label='documents', model_name='Document')
    Workflow = apps.get_model(
        app_label='document_states', model_name='Workflow'
    )

    logger.info('Start launching workflows')
    for document in Document.objects.all():
        logger.debug('Lauching workflows for document ID: %d', document.pk)
        Workflow.objects.launch_for(document=document)

    logger.info('Finished launching workflows')
