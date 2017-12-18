# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0005_auto_20150729_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadatatype',
            name='parser',
            field=models.CharField(
                blank=True, help_text='The parser will reformat the value '
                'entered to conform to the expected format.', max_length=64,
                verbose_name='Parser',
                choices=[
                    (
                        b'metadata.validators.DateAndTimeValidator',
                        b'metadata.validators.DateAndTimeValidator'
                    ), (
                        b'metadata.validators.DateValidator',
                        b'metadata.validators.DateValidator'
                    ), (
                        b'metadata.validators.TimeValidator',
                        b'metadata.validators.TimeValidator'
                    )
                ]
            ), preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metadatatype',
            name='validation',
            field=models.CharField(
                blank=True, help_text='The validator will reject data entry '
                'if the value entered does not conform to the expected '
                'format.', max_length=64, verbose_name='Validator',
                choices=[
                    (
                        b'metadata.validators.DateAndTimeValidator',
                        b'metadata.validators.DateAndTimeValidator'
                    ), (
                        b'metadata.validators.DateValidator',
                        b'metadata.validators.DateValidator'
                    ), (
                        b'metadata.validators.TimeValidator',
                        b'metadata.validators.TimeValidator'
                    )
                ]
            ), preserve_default=True,
        ),
    ]
