# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'creation_datetime', models.DateTimeField(
                        auto_now_add=True, verbose_name='Creation datetime'
                    )
                ),
                (
                    'timeout', models.IntegerField(
                        default=30, verbose_name='Timeout'
                    )
                ),
                (
                    'name', models.CharField(
                        unique=True, max_length=48, verbose_name='Name'
                    )
                ),
            ],
            options={
                'verbose_name': 'Lock',
                'verbose_name_plural': 'Locks',
            },
            bases=(models.Model,),
        ),
    ]
