# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gpg', '0002_auto_20160322_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='algorithm',
            field=models.PositiveIntegerField(
                verbose_name='Algorithm', editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='creation_date',
            field=models.DateField(
                verbose_name='Creation date', editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='expiration_date',
            field=models.DateField(
                verbose_name='Expiration date', null=True, editable=False,
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='fingerprint',
            field=models.CharField(
                verbose_name='Fingerprint', unique=True, max_length=40,
                editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='key_data',
            field=models.TextField(verbose_name='Key data', editable=False),
        ),
        migrations.AlterField(
            model_name='key',
            name='key_id',
            field=models.CharField(
                verbose_name='Key ID', unique=True, max_length=16,
                editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='key_type',
            field=models.CharField(
                verbose_name='Type', max_length=3, editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='length',
            field=models.PositiveIntegerField(
                verbose_name='Length', editable=False
            ),
        ),
        migrations.AlterField(
            model_name='key',
            name='user_id',
            field=models.TextField(verbose_name='User ID', editable=False),
        ),
    ]
