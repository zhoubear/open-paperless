from __future__ import unicode_literals

import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .classes import BaseTransformation
from .managers import TransformationManager
from .validators import YAMLValidator

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Transformation(models.Model):
    """
    Model that stores the transformation and transformation arguments
    for a given object
    Fields:
    * order - Order of a Transformation - In case there are multiple
    transformations for an object, this field list the order at which
    they will be execute.
    * arguments - Arguments of a Transformation - An optional field to hold a
    transformation argument. Example: if a page is rotated with the Rotation
    transformation, this field will show by how many degrees it was rotated.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    order = models.PositiveIntegerField(
        blank=True, db_index=True, default=0, help_text=_(
            'Order in which the transformations will be executed. If left '
            'unchanged, an automatic order value will be assigned.'
        ), verbose_name=_('Order')
    )
    name = models.CharField(
        choices=BaseTransformation.get_transformation_choices(),
        max_length=128, verbose_name=_('Name')
    )
    arguments = models.TextField(
        blank=True, help_text=_(
            'Enter the arguments for the transformation as a YAML '
            'dictionary. ie: {"degrees": 180}'
        ), validators=[YAMLValidator()], verbose_name=_('Arguments')
    )

    objects = TransformationManager()

    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Transformation.objects.filter(
                content_type=self.content_type, object_id=self.object_id
            ).aggregate(Max('order'))['order__max']
            if last_order is not None:
                self.order = last_order + 1
        super(Transformation, self).save(*args, **kwargs)

    class Meta:
        ordering = ('order',)
        unique_together = ('content_type', 'object_id', 'order')
        verbose_name = _('Transformation')
        verbose_name_plural = _('Transformations')
