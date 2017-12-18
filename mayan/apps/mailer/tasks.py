from __future__ import unicode_literals

from django.apps import apps

from mayan.celery import app


@app.task(ignore_result=True)
def task_send_document(subject_text, body_text_content, sender, recipient, user_mailer_id, as_attachment=False, document_id=None):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    UserMailer = apps.get_model(
        app_label='mailer', model_name='UserMailer'
    )

    if document_id:
        document = Document.objects.get(pk=document_id)
    else:
        document = None

    user_mailer = UserMailer.objects.get(pk=user_mailer_id)

    user_mailer.send(
        subject=subject_text, body=body_text_content, to=recipient,
        document=document, as_attachment=as_attachment
    )
