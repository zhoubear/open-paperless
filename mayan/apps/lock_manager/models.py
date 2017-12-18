from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import LockManager
from .settings import setting_default_lock_timeout


@python_2_unicode_compatible
class Lock(models.Model):
    creation_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Creation datetime')
    )
    timeout = models.IntegerField(
        default=setting_default_lock_timeout.value, verbose_name=_('Timeout')
    )
    name = models.CharField(
        max_length=64, unique=True, verbose_name=_('Name')
    )

    objects = LockManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.timeout and not kwargs.get('timeout'):
            self.timeout = setting_default_lock_timeout.value

        super(Lock, self).save(*args, **kwargs)

    def release(self):
        try:
            lock = Lock.objects.get(
                name=self.name, creation_datetime=self.creation_datetime
            )
        except Lock.DoesNotExist:
            # Our lock has expired and was reassigned
            pass
        else:
            lock.delete()

    class Meta:
        verbose_name = _('Lock')
        verbose_name_plural = _('Locks')
