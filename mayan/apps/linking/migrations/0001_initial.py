# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartLink',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'title', models.CharField(
                        max_length=96, verbose_name='Title'
                    )
                ),
                (
                    'dynamic_title', models.CharField(
                        help_text='This expression will be evaluated against '
                        'the current selected document.', max_length=96,
                        verbose_name='Dynamic title', blank=True
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
                (
                    'document_types', models.ManyToManyField(
                        to='documents.DocumentType',
                        verbose_name='Document types'
                    )
                ),
            ],
            options={
                'verbose_name': 'Smart link',
                'verbose_name_plural': 'Smart links',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SmartLinkCondition',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'inclusion', models.CharField(
                        default='&', help_text='The inclusion is ignored for '
                        'the first item.', max_length=16, choices=[
                            ('&', 'and'), ('|', 'or')
                        ]
                    )
                ),
                (
                    'foreign_document_data', models.CharField(
                        help_text='This represents the metadata of all other '
                        'documents.', max_length=128,
                        verbose_name='Foreign document attribute'
                    )
                ),
                (
                    'operator', models.CharField(
                        max_length=16, choices=[
                            ('exact', 'is equal to'),
                            ('iexact', 'is equal to (case insensitive)'),
                            ('contains', 'contains'),
                            ('icontains', 'contains (case insensitive)'),
                            ('in', 'is in'), ('gt', 'is greater than'),
                            ('gte', 'is greater than or equal to'),
                            ('lt', 'is less than'),
                            ('lte', 'is less than or equal to'),
                            ('startswith', 'starts with'),
                            ('istartswith', 'starts with (case insensitive)'),
                            ('endswith', 'ends with'),
                            ('iendswith', 'ends with (case insensitive)'),
                            ('regex', 'is in regular expression'),
                            (
                                'iregex',
                                'is in regular expression (case insensitive)'
                            )
                        ]
                    )
                ),
                (
                    'expression', models.TextField(
                        help_text='This expression will be evaluated against '
                        'the current document.', verbose_name='Expression'
                    )
                ),
                (
                    'negated', models.BooleanField(
                        default=False, help_text='Inverts the logic of the '
                        'operator.', verbose_name='Negated'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
                (
                    'smart_link', models.ForeignKey(
                        related_name='conditions', verbose_name='Smart link',
                        to='linking.SmartLink'
                    )
                ),
            ],
            options={
                'verbose_name': 'Link condition',
                'verbose_name_plural': 'Link conditions',
            },
            bases=(models.Model,),
        ),
    ]
