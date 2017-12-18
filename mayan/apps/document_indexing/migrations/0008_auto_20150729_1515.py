# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0007_auto_20150729_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexinstancenode',
            name='value',
            field=models.CharField(
                db_index=True, max_length=128, verbose_name='Value',
                blank=True
            ),
            preserve_default=True,
        ),
    ]
