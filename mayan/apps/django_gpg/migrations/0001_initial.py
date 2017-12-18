# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                ('data', models.TextField(verbose_name='Data')),
                (
                    'key_id', models.CharField(
                        unique=True, max_length=16, verbose_name='Key ID'
                    )
                ),
                (
                    'creation_date', models.DateField(
                        verbose_name='Creation date'
                    )
                ),
                (
                    'expiration_date', models.DateField(
                        null=True, verbose_name='Expiration date', blank=True
                    )
                ),
                (
                    'fingerprint', models.CharField(
                        unique=True, max_length=40, verbose_name='Fingerprint'
                    )
                ),
                ('length', models.PositiveIntegerField(verbose_name='Length')),
                (
                    'algorithm', models.PositiveIntegerField(
                        verbose_name='Algorithm'
                    )
                ),
                ('user_id', models.TextField(verbose_name='User ID')),
                (
                    'key_type', models.CharField(
                        max_length=3, verbose_name='Type'
                    )
                ),
            ],
            options={
                'verbose_name': 'Key',
                'verbose_name_plural': 'Keys',
            },
        ),
    ]
