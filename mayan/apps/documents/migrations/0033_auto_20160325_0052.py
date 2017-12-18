# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0032_auto_20160315_0537'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttypefilename',
            options={
                'ordering': ('filename',), 'verbose_name': 'Quick label',
                'verbose_name_plural': 'Quick labels'
            },
        ),
    ]
