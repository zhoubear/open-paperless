# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0029_auto_20160122_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttype',
            name='delete_time_period',
            field=models.PositiveIntegerField(
                default=30, help_text='Amount of time after which documents '
                'of this type in the trash will be deleted.', null=True,
                verbose_name='Delete time period', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='delete_time_unit',
            field=models.CharField(
                default='days', choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ], max_length=8, blank=True, null=True,
                verbose_name='Delete time unit'
            ),
        ),
    ]
