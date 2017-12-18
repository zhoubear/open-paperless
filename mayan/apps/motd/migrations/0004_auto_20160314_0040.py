# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motd', '0003_auto_20160313_0349'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MessageOfTheDay',
            new_name='Message',
        ),
        migrations.AlterModelOptions(
            name='message',
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages'
            },
        ),
    ]
