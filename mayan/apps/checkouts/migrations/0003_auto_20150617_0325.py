# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_from_content_type_user_to_foreign_key_field_user(apps, schema_editor):
    # The model references the use who checked out the document using a
    # generic.GenericForeignKey. This migrations changes that to a simpler
    # ForeignKey to the User model

    DocumentCheckout = apps.get_model('checkouts', 'DocumentCheckout')

    for document_checkout in DocumentCheckout.objects.all():
        document_checkout.user = document_checkout.user_object
        document_checkout.save()


class Migration(migrations.Migration):

    dependencies = [
        ('checkouts', '0002_documentcheckout_user'),
    ]

    operations = [
        migrations.RunPython(
            move_from_content_type_user_to_foreign_key_field_user
        ),
    ]
