# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0017_auto_20150714_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(
                default='', verbose_name='Description', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='label',
            field=models.CharField(
                default='', max_length=255, blank=True,
                help_text='The name of the document', verbose_name='Label',
                db_index=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='comment',
            field=models.TextField(
                default='', verbose_name='Comment', blank=True
            ),
            preserve_default=True,
        ),
    ]
