# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Index',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'name', models.CharField(
                        help_text='Internal name used to reference this '
                        'index.', unique=True, max_length=64,
                        verbose_name='Name'
                    )
                ),
                (
                    'title', models.CharField(
                        help_text='The name that will be visible to users.',
                        unique=True, max_length=128, verbose_name='Title'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, help_text='Causes this index to be '
                        'visible and updated when document data changes.',
                        verbose_name='Enabled'
                    )
                ),
                (
                    'document_types',
                    models.ManyToManyField(
                        to='documents.DocumentType',
                        verbose_name='Document types'
                    )
                ),
            ],
            options={
                'verbose_name': 'Index',
                'verbose_name_plural': 'Indexes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndexInstanceNode',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'value', models.CharField(
                        max_length=128, verbose_name='Value', blank=True
                    )
                ),
                (
                    'lft', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'rght', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'tree_id', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'level', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'documents', models.ManyToManyField(
                        related_name='node_instances',
                        verbose_name='Documents', to='documents.Document'
                    )
                ),
            ],
            options={
                'verbose_name': 'Index node instance',
                'verbose_name_plural': 'Indexes node instances',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndexTemplateNode',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'expression', models.CharField(
                        help_text='Enter a python string expression to be '
                        'evaluated.', max_length=128,
                        verbose_name='Indexing expression'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, help_text='Causes this node to be '
                        'visible and updated when document data changes.',
                        verbose_name='Enabled'
                    )
                ),
                (
                    'link_documents', models.BooleanField(
                        default=False, help_text='Check this option to have '
                        'this node act as a container for documents and not '
                        'as a parent for further nodes.',
                        verbose_name='Link documents'
                    )
                ),
                (
                    'lft', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'rght', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'tree_id', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'level', models.PositiveIntegerField(
                        editable=False, db_index=True
                    )
                ),
                (
                    'index', models.ForeignKey(
                        related_name='node_templates', verbose_name='Index',
                        to='document_indexing.Index'
                    )
                ),
                (
                    'parent', mptt.fields.TreeForeignKey(
                        blank=True, to='document_indexing.IndexTemplateNode',
                        null=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Index node template',
                'verbose_name_plural': 'Indexes node template',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='indexinstancenode',
            name='index_template_node',
            field=models.ForeignKey(
                related_name='node_instance',
                verbose_name='Index template node',
                to='document_indexing.IndexTemplateNode'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='indexinstancenode',
            name='parent',
            field=mptt.fields.TreeForeignKey(
                blank=True, to='document_indexing.IndexInstanceNode',
                null=True
            ),
            preserve_default=True,
        ),
    ]
