# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motd', '0002_auto_20160313_0340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageoftheday',
            name='message',
            field=models.TextField(verbose_name='Message'),
        ),
    ]
