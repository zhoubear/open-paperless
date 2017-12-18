from __future__ import unicode_literals

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class ErrorLogEntryManager(models.Manager):
    def register(self, model):
        ErrorLogEntry = apps.get_model(
            app_label='common', model_name='ErrorLogEntry'
        )
        model.add_to_class('error_logs', GenericRelation(ErrorLogEntry))
