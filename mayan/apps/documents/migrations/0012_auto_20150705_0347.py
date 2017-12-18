# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0011_auto_20150704_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='deleted_date_time',
            field=models.DateTimeField(
                null=True, verbose_name='Date and time trashed', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='delete_time_period',
            field=models.PositiveIntegerField(
                default=30, help_text='Amount of time after which documents '
                'of this type in the trash will be deleted.',
                verbose_name='Delete time period'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='delete_time_unit',
            field=models.CharField(
                default='days', max_length=8, verbose_name='Delete time unit',
                choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='trash_time_period',
            field=models.PositiveIntegerField(
                help_text='Amount of time after which documents of this type '
                'will be moved to the trash.', null=True,
                verbose_name='Trash time period', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='trash_time_unit',
            field=models.CharField(
                blank=True, max_length=8, null=True,
                verbose_name='Trash time unit', choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ]
            ),
            preserve_default=True,
        ),
    ]
