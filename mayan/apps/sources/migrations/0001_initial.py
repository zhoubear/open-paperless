# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'title', models.CharField(
                        max_length=64, verbose_name='Title'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutOfProcessSource',
            fields=[
                (
                    'source_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.Source'
                    )
                ),
            ],
            options={
                'verbose_name': 'Out of process',
                'verbose_name_plural': 'Out of process',
            },
            bases=('sources.source',),
        ),
        migrations.CreateModel(
            name='IntervalBaseModel',
            fields=[
                (
                    'outofprocesssource_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.OutOfProcessSource'
                    )
                ),
                (
                    'interval', models.PositiveIntegerField(
                        default=600, help_text='Interval in seconds between '
                        'checks for new documents.', verbose_name='Interval'
                    )
                ),
                (
                    'uncompress', models.CharField(
                        help_text='Whether to expand or not, compressed '
                        'archives.', max_length=1, verbose_name='Uncompress',
                        choices=[('y', 'Always'), ('n', 'Never')]
                    )
                ),
            ],
            options={
                'verbose_name': 'Interval source',
                'verbose_name_plural': 'Interval sources',
            },
            bases=('sources.outofprocesssource',),
        ),
        migrations.CreateModel(
            name='EmailBaseModel',
            fields=[
                (
                    'intervalbasemodel_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.IntervalBaseModel'
                    )
                ),
                (
                    'host', models.CharField(
                        max_length=128, verbose_name='Host'
                    )
                ),
                (
                    'ssl', models.BooleanField(
                        default=True, verbose_name='SSL'
                    )
                ),
                (
                    'port', models.PositiveIntegerField(
                        help_text='Typical choices are 110 for POP3, 995 for '
                        'POP3 over SSL, 143 for IMAP, 993 for IMAP over SSL.',
                        null=True, verbose_name='Port', blank=True
                    )
                ),
                (
                    'username', models.CharField(
                        max_length=96, verbose_name='Username'
                    )
                ),
                (
                    'password', models.CharField(
                        max_length=96, verbose_name='Password'
                    )
                ),
            ],
            options={
                'verbose_name': 'Email source',
                'verbose_name_plural': 'Email sources',
            },
            bases=('sources.intervalbasemodel',),
        ),
        migrations.CreateModel(
            name='POP3Email',
            fields=[
                (
                    'emailbasemodel_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.EmailBaseModel'
                    )
                ),
                (
                    'timeout', models.PositiveIntegerField(
                        default=60, verbose_name='Timeout'
                    )
                ),
            ],
            options={
                'verbose_name': 'POP email',
                'verbose_name_plural': 'POP email',
            },
            bases=('sources.emailbasemodel',),
        ),
        migrations.CreateModel(
            name='IMAPEmail',
            fields=[
                (
                    'emailbasemodel_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.EmailBaseModel'
                    )
                ),
                (
                    'mailbox', models.CharField(
                        default='INBOX', help_text='Mail from which to check '
                        'for messages with attached documents.',
                        max_length=64, verbose_name='Mailbox'
                    )
                ),
            ],
            options={
                'verbose_name': 'IMAP email',
                'verbose_name_plural': 'IMAP email',
            },
            bases=('sources.emailbasemodel',),
        ),
        migrations.CreateModel(
            name='InteractiveSource',
            fields=[
                (
                    'source_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.Source'
                    )
                ),
            ],
            options={
                'verbose_name': 'Interactive source',
                'verbose_name_plural': 'Interactive sources',
            },
            bases=('sources.source',),
        ),
        migrations.CreateModel(
            name='SourceTransformation',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'object_id', models.PositiveIntegerField()
                ),
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
                            ('resize', 'Resize'), ('rotate', 'Rotate'),
                            ('zoom', 'Zoom')
                        ]
                    )
                ),
                (
                    'arguments', models.TextField(
                        blank=True, help_text="Use dictionaries to indentify "
                        "arguments, example: {'degrees':90}", null=True,
                        verbose_name='Arguments', validators=[]
                    )
                ),
                (
                    'content_type', models.ForeignKey(
                        to='contenttypes.ContentType'
                    )
                ),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Document source transformation',
                'verbose_name_plural': 'Document source transformations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StagingFolderSource',
            fields=[
                (
                    'interactivesource_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.InteractiveSource'
                    )
                ),
                (
                    'folder_path', models.CharField(
                        help_text='Server side filesystem path.',
                        max_length=255, verbose_name='Folder path'
                    )
                ),
                (
                    'preview_width', models.IntegerField(
                        help_text='Width value to be passed to the converter '
                        'backend.', verbose_name='Preview width'
                    )
                ),
                (
                    'preview_height', models.IntegerField(
                        help_text='Height value to be passed to the '
                        'converter backend.', null=True,
                        verbose_name='Preview height', blank=True
                    )
                ),
                (
                    'uncompress', models.CharField(
                        help_text='Whether to expand or not compressed '
                        'archives.', max_length=1, verbose_name='Uncompress',
                        choices=[
                            ('y', 'Always'), ('n', 'Never'), ('a', 'Ask user')
                        ]
                    )
                ),
                (
                    'delete_after_upload', models.BooleanField(
                        default=True, help_text='Delete the file after is '
                        'has been successfully uploaded.',
                        verbose_name='Delete after upload'
                    )
                ),
            ],
            options={
                'verbose_name': 'Staging folder',
                'verbose_name_plural': 'Staging folders',
            },
            bases=('sources.interactivesource',),
        ),
        migrations.CreateModel(
            name='WatchFolderSource',
            fields=[
                (
                    'intervalbasemodel_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.IntervalBaseModel'
                    )
                ),
                (
                    'folder_path', models.CharField(
                        help_text='Server side filesystem path.',
                        max_length=255, verbose_name='Folder path'
                    )
                ),
            ],
            options={
                'verbose_name': 'Watch folder',
                'verbose_name_plural': 'Watch folders',
            },
            bases=('sources.intervalbasemodel',),
        ),
        migrations.CreateModel(
            name='WebFormSource',
            fields=[
                (
                    'interactivesource_ptr', models.OneToOneField(
                        parent_link=True, auto_created=True, primary_key=True,
                        serialize=False, to='sources.InteractiveSource'
                    )
                ),
                (
                    'uncompress', models.CharField(
                        help_text='Whether to expand or not compressed '
                        'archives.', max_length=1, verbose_name='Uncompress',
                        choices=[
                            ('y', 'Always'), ('n', 'Never'), ('a', 'Ask user')
                        ]
                    )
                ),
            ],
            options={
                'verbose_name': 'Web form',
                'verbose_name_plural': 'Web forms',
            },
            bases=('sources.interactivesource',),
        ),
        migrations.AddField(
            model_name='intervalbasemodel',
            name='document_type',
            field=models.ForeignKey(
                verbose_name='Document type', to='documents.DocumentType',
                help_text='Assign a document type to documents uploaded from '
                'this source.'
            ),
            preserve_default=True,
        ),
    ]
