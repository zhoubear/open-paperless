# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gpg', '0003_auto_20160322_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='key_data',
            field=models.TextField(verbose_name='Key data'),
        ),
        migrations.AlterField(
            model_name='key',
            name='key_type',
            field=models.CharField(
                verbose_name='Type', max_length=3, editable=False,
                choices=[('pub', 'Public'), ('sec', 'Secret')]
            ),
        ),
    ]
