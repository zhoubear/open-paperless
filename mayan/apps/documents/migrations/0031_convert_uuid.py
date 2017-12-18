# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import migrations


def convert_uuid_to_hex(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')

    for document in Document.objects.all():
        document.uuid = uuid.UUID(document.uuid).hex
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0030_auto_20160309_1837'),
    ]

    operations = [
        migrations.RunPython(convert_uuid_to_hex),
    ]
