# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecentSearch',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'query', models.TextField(
                        verbose_name='Query', editable=False
                    )
                ),
                (
                    'datetime_created', models.DateTimeField(
                        auto_now=True, verbose_name='Datetime created',
                        db_index=True
                    )
                ),
                (
                    'hits', models.IntegerField(
                        verbose_name='Hits', editable=False
                    )
                ),
                (
                    'user', models.ForeignKey(
                        verbose_name='User', to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
            options={
                'ordering': ('-datetime_created',),
                'verbose_name': 'Recent search',
                'verbose_name_plural': 'Recent searches',
            },
            bases=(models.Model,),
        ),
    ]
