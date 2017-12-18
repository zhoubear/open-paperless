# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_signatures', '0003_auto_20160325_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversionsignature',
            name='document_version',
            field=models.ForeignKey(
                editable=False, to='documents.DocumentVersion',
                verbose_name='Document version'
            ),
        ),
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='date',
            field=models.DateField(
                verbose_name='Date signed', null=True, editable=False,
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='document_version',
            field=models.ForeignKey(
                related_name='signatures', editable=False,
                to='documents.DocumentVersion', verbose_name='Document version'
            ),
        ),
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='public_key_fingerprint',
            field=models.CharField(
                null=True, editable=False, max_length=40, blank=True,
                unique=True, verbose_name='Public key fingerprint'
            ),
        ),
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='signature_id',
            field=models.CharField(
                verbose_name='Signature ID', max_length=64, null=True,
                editable=False, blank=True
            ),
        ),
    ]
