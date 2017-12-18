# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCheckout',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'checkout_datetime',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Check out date and time'
                    )
                ),
                (
                    'expiration_datetime',
                    models.DateTimeField(
                        help_text='Amount of time to hold the document '
                        'checked out in minutes.',
                        verbose_name='Check out expiration date and time'
                    )
                ),
                (
                    'user_object_id',
                    models.PositiveIntegerField(null=True, blank=True)
                ),
                (
                    'block_new_version',
                    models.BooleanField(
                        default=True,
                        help_text='Do not allow new version of this document '
                        'to be uploaded.',
                        verbose_name='Block new version upload'
                    )
                ),
                (
                    'document',
                    models.ForeignKey(
                        verbose_name='Document', to='documents.Document',
                        unique=True
                    )
                ),
                (
                    'user_content_type',
                    models.ForeignKey(
                        blank=True, to='contenttypes.ContentType', null=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Document checkout',
                'verbose_name_plural': 'Document checkouts',
            },
            bases=(models.Model,),
        ),
    ]
