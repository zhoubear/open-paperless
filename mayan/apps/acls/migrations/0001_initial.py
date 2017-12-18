# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('permissions', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessEntry',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'holder_id', models.PositiveIntegerField()
                ),
                ('object_id', models.PositiveIntegerField()),
                (
                    'content_type', models.ForeignKey(
                        related_name='object_content_type',
                        to='contenttypes.ContentType'
                    )
                ),
                (
                    'holder_type', models.ForeignKey(
                        related_name='access_holder',
                        to='contenttypes.ContentType'
                    )
                ),
                (
                    'permission', models.ForeignKey(
                        verbose_name='Permission',
                        to='permissions.StoredPermission'
                    )
                ),
            ],
            options={
                'verbose_name': 'Access entry',
                'verbose_name_plural': 'Access entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreatorSingleton',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Creator',
                'verbose_name_plural': 'Creator',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultAccessEntry',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                ('holder_id', models.PositiveIntegerField()),
                (
                    'content_type', models.ForeignKey(
                        related_name='default_access_entry_class',
                        to='contenttypes.ContentType'
                    )
                ),
                (
                    'holder_type', models.ForeignKey(
                        related_name='default_access_entry_holder',
                        to='contenttypes.ContentType'
                    )
                ),
                (
                    'permission', models.ForeignKey(
                        verbose_name='Permission',
                        to='permissions.StoredPermission'
                    )
                ),
            ],
            options={
                'verbose_name': 'Default access entry',
                'verbose_name_plural': 'Default access entries',
            },
            bases=(models.Model,),
        ),
    ]
