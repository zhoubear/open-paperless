# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import converter.validators


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0004_auto_20150704_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='arguments',
            field=models.TextField(
                help_text='Enter the arguments for the transformation as a '
                'YAML dictionary. ie: {"degrees": 180}', blank=True,
                verbose_name='Arguments',
                validators=[converter.validators.YAMLValidator()]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transformation',
            name='name',
            field=models.CharField(
                max_length=128, verbose_name='Name', choices=[
                    ('rotate', 'Rotate: degrees'), ('zoom', 'Zoom: percent'),
                    ('resize', 'Resize: width, height')
                ]
            ),
            preserve_default=True,
        ),
    ]
