# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageOfTheDay',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'label', models.CharField(
                        max_length=32, verbose_name='Label'
                    )
                ),
                (
                    'message', models.TextField(
                        verbose_name='Message', blank=True
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
                (
                    'start_datetime', models.DateTimeField(
                        verbose_name='Start date time', blank=True
                    )
                ),
                (
                    'end_datetime', models.DateTimeField(
                        verbose_name='End date time', blank=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Message of the day',
                'verbose_name_plural': 'Messages of the day',
            },
        ),
    ]
