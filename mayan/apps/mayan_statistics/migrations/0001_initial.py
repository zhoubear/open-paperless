# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticResult',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                ('slug', models.SlugField(verbose_name='Slug')),
                (
                    'datetime', models.DateTimeField(
                        auto_now=True, verbose_name='Date time'
                    )
                ),
                (
                    'serialize_data', models.TextField(
                        verbose_name='Data', blank=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Statistics result',
                'verbose_name_plural': 'Statistics results',
            },
            bases=(models.Model,),
        ),
    ]
