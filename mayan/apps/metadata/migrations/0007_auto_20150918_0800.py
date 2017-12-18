# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0006_auto_20150820_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatatype',
            name='parser',
            field=models.CharField(
                blank=True, help_text='The parser will reformat the value '
                'entered to conform to the expected format.', max_length=64,
                verbose_name='Parser',
                choices=[
                    (
                        b'metadata.parsers.DateAndTimeParser',
                        b'metadata.parsers.DateAndTimeParser'
                    ), (
                        b'metadata.parsers.DateParser',
                        b'metadata.parsers.DateParser'
                    ), (
                        b'metadata.parsers.TimeParser',
                        b'metadata.parsers.TimeParser'
                    )
                ]
            ), preserve_default=True,
        ),
    ]
