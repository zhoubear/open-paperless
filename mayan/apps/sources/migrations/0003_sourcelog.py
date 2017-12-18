# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0002_auto_20150608_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceLog',
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
                (
                    'source', models.ForeignKey(
                        related_name='logs', verbose_name='Source',
                        to='sources.Source'
                    )
                ),
            ],
            options={
                'ordering': ['-datetime'],
                'get_latest_by': 'datetime',
                'verbose_name': 'Log entry',
                'verbose_name_plural': 'Log entries',
            },
            bases=(models.Model,),
        ),
    ]
