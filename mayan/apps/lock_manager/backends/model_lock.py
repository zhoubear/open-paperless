from __future__ import unicode_literals

from django.apps import apps

from .base import LockingBackend


class ModelLock(LockingBackend):
    @classmethod
    def acquire_lock(cls, name, timeout=None):
        super(ModelLock, cls).acquire_lock(name=name, timeout=timeout)
        Lock = apps.get_model(app_label='lock_manager', model_name='Lock')
        return ModelLock(
            model_instance=Lock.objects.acquire_lock(
                name=name, timeout=timeout
            )
        )

    @classmethod
    def purge_locks(cls):
        super(ModelLock, cls).purge_locks()
        Lock = apps.get_model(app_label='lock_manager', model_name='Lock')
        Lock.objects.select_for_update().delete()

    def __init__(self, model_instance):
        self.model_instance = model_instance
        self.name = model_instance.name

    def release(self):
        super(ModelLock, self).release()
        self.model_instance.release()
