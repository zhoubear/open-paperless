# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0006_auto_20150708_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailbasemodel',
            name='metadata_attachment_name',
            field=models.CharField(
                default='metadata.yaml', help_text='Name of the attachment '
                'that will contains the metadata types and values to be '
                'assigned to the rest of the downloaded attachments.',
                max_length=128, verbose_name='Metadata attachment name'
            ),
            preserve_default=True,
        ),
    ]
