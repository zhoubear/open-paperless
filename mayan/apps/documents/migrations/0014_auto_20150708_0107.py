# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0013_document_is_stub'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={
                'ordering': ('label',), 'verbose_name': 'Document type',
                'verbose_name_plural': 'Documents types'
            },
        ),
        migrations.RenameField(
            model_name='documenttype',
            old_name='name',
            new_name='label',
        ),
    ]
