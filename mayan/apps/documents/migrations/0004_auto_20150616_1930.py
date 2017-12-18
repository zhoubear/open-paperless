# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20150608_1915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={
                'ordering': ('-date_added',), 'verbose_name': 'Document',
                'verbose_name_plural': 'Documents'
            },
        ),
        migrations.AlterModelOptions(
            name='documentpage',
            options={
                'ordering': ('page_number',), 'verbose_name': 'Document page',
                'verbose_name_plural': 'Document pages'
            },
        ),
        migrations.AlterModelOptions(
            name='documenttype',
            options={
                'ordering': ('name',), 'verbose_name': 'Document type',
                'verbose_name_plural': 'Documents types'
            },
        ),
        migrations.AlterModelOptions(
            name='documenttypefilename',
            options={
                'ordering': ('filename',),
                'verbose_name': 'Document type quick rename filename',
                'verbose_name_plural': 'Document types quick rename filenames'
            },
        ),
    ]
