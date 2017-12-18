# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'datetime', models.DateTimeField(
                        auto_now_add=True, verbose_name='Date time'
                    )
                ),
                (
                    'message', models.TextField(
                        verbose_name='Message', editable=False, blank=True
                    )
                ),
            ],
            options={
                'ordering': ('-datetime',),
                'get_latest_by': 'datetime',
                'verbose_name': 'Log entry',
                'verbose_name_plural': 'Log entries',
            },
            bases=(models.Model,),
        ),
    ]
