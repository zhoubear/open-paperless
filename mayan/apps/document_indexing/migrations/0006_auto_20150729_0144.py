# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.template.defaultfilters import slugify


def assign_slugs(apps, schema_editor):
    Index = apps.get_model('document_indexing', 'Index')

    for index in Index.objects.all():
        index.slug = slugify(index.label)
        index.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0005_index_slug'),
    ]

    operations = [
        migrations.RunPython(assign_slugs),
    ]
