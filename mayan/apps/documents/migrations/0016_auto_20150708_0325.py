# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0015_auto_20150708_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(
                default='', verbose_name='Description', blank=True
            ),
            preserve_default=False,
        ),
    ]
