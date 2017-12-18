# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_auto_20150617_0358'),
        ('ocr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentPageContent',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'content', models.TextField(
                        verbose_name='Content', blank=True
                    )
                ),
                (
                    'document_page', models.OneToOneField(
                        related_name='ocr_content',
                        verbose_name='Document page',
                        to='documents.DocumentPage'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document page content',
                'verbose_name_plural': 'Document pages contents',
            },
            bases=(models.Model,),
        ),
    ]
