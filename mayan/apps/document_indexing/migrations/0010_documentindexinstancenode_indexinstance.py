# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0009_auto_20150815_0351'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentIndexInstanceNode',
            fields=[
            ],
            options={
                'verbose_name': 'Document index node instance',
                'proxy': True,
                'verbose_name_plural': 'Document indexes node instances',
            },
            bases=('document_indexing.indexinstancenode',),
        ),
        migrations.CreateModel(
            name='IndexInstance',
            fields=[
            ],
            options={
                'verbose_name': 'Index instance',
                'proxy': True,
                'verbose_name_plural': 'Index instances',
            },
            bases=('document_indexing.index',),
        ),
    ]
