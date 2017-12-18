# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0009_auto_20150714_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='name',
            field=models.CharField(
                max_length=128, verbose_name='Name',
                choices=[
                    ('rotate', 'Rotate: degrees'), ('zoom', 'Zoom: percent'),
                    ('resize', 'Resize: width, height'),
                    ('crop', 'Crop: left, top, right, bottom')
                ]
            ),
            preserve_default=True,
        ),
    ]
