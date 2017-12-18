# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_auto_20150708_0118'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metadatatype',
            options={
                'ordering': ('label',), 'verbose_name': 'Metadata type',
                'verbose_name_plural': 'Metadata types'
            },
        ),
        migrations.RenameField(
            model_name='metadatatype',
            old_name='title',
            new_name='label',
        ),
    ]
