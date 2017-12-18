# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0007_emailbasemodel_metadata_attachment_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailbasemodel',
            name='metadata_attachment_name',
            field=models.CharField(
                default='metadata.yaml', help_text='Name of the attachment '
                'that will contains the metadata type names and value pairs '
                'to be assigned to the rest of the downloaded attachments. '
                'Note: This attachment has to be the first attachment.',
                max_length=128, verbose_name='Metadata attachment name'
            ),
            preserve_default=True,
        ),
    ]
