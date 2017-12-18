# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatatype',
            name='validation',
            field=models.CharField(
                blank=True, max_length=64,
                verbose_name='Validation function name',
                choices=[
                    (
                        b'metadata.validators.DateAndTimeValidator',
                        b'metadata.validators.DateAndTimeValidator'
                    ),
                    (
                        b'metadata.validators.DateValidator',
                        b'metadata.validators.DateValidator'
                    ),
                    (
                        b'metadata.validators.TimeValidator',
                        b'metadata.validators.TimeValidator'
                    )
                ]
            ),
            preserve_default=True,
        ),
    ]
