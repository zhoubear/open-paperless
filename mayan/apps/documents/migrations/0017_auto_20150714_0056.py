# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0016_auto_20150708_0325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date_added',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='Added', db_index=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='timestamp',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='Timestamp', db_index=True
            ),
            preserve_default=True,
        ),
    ]
