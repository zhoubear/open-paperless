# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentMetadata',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'value', models.CharField(
                        db_index=True, max_length=255, null=True,
                        verbose_name='Value', blank=True
                    )
                ),
                (
                    'document', models.ForeignKey(
                        related_name='metadata', verbose_name='Document',
                        to='documents.Document'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document metadata',
                'verbose_name_plural': 'Document metadata',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentTypeMetadataType',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'required', models.BooleanField(
                        default=False, verbose_name='Required'
                    )
                ),
                (
                    'document_type', models.ForeignKey(
                        related_name='metadata',
                        verbose_name='Document type',
                        to='documents.DocumentType'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document type metadata type options',
                'verbose_name_plural': 'Document type metadata types options',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MetadataType',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'name', models.CharField(
                        help_text='Do not use python reserved words, '
                        'or spaces.', unique=True, max_length=48,
                        verbose_name='Name'
                    )
                ),
                (
                    'title', models.CharField(
                        max_length=48, verbose_name='Title'
                    )
                ),
                (
                    'default', models.CharField(
                        help_text='Enter a string to be evaluated.',
                        max_length=128, null=True, verbose_name='Default',
                        blank=True
                    )
                ),
                (
                    'lookup', models.TextField(
                        help_text='Enter a string to be evaluated that '
                        'returns an iterable.', null=True,
                        verbose_name='Lookup', blank=True)
                ),
                (
                    'validation', models.CharField(
                        blank=True, max_length=64,
                        verbose_name='Validation function name',
                        choices=[
                            ('Parse date', 'Parse date'),
                            ('Parse date and time', 'Parse date and time'),
                            ('Parse time', 'Parse time')
                        ]
                    )
                ),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Metadata type',
                'verbose_name_plural': 'Metadata types',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='documenttypemetadatatype',
            name='metadata_type',
            field=models.ForeignKey(
                verbose_name='Metadata type', to='metadata.MetadataType'
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='documenttypemetadatatype',
            unique_together=set([('document_type', 'metadata_type')]),
        ),
        migrations.AddField(
            model_name='documentmetadata',
            name='metadata_type',
            field=models.ForeignKey(
                verbose_name='Type', to='metadata.MetadataType'
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='documentmetadata',
            unique_together=set([('document', 'metadata_type')]),
        ),
    ]
