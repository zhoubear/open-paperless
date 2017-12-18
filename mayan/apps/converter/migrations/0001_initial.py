# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import converter.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transformation',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                ('object_id', models.PositiveIntegerField()),
                (
                    'order', models.PositiveIntegerField(
                        default=0, null=True, verbose_name='Order',
                        db_index=True, blank=True
                    )
                ),
                (
                    'transformation', models.CharField(
                        max_length=128, verbose_name='Transformation',
                        choices=[
                            ('rotate', 'Rotate'), ('zoom', 'Zoom'),
                            ('resize', 'Resize')
                        ]
                    )
                ),
                (
                    'arguments', models.TextField(
                        blank=True, null=True, verbose_name='Arguments',
                        validators=[converter.validators.YAMLValidator]
                    )
                ),
                (
                    'content_type',
                    models.ForeignKey(to='contenttypes.ContentType')
                ),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Transformation',
                'verbose_name_plural': 'Transformations',
            },
            bases=(models.Model,),
        ),
    ]
