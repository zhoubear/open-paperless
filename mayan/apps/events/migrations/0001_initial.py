# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventType',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'name', models.CharField(
                        unique=True, max_length=64, verbose_name='Name'
                    )
                ),
            ],
            options={
                'verbose_name': 'Event type',
                'verbose_name_plural': 'Event types',
            },
            bases=(models.Model,),
        ),
    ]
