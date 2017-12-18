from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from celery.five import monotonic
from celery.task.control import inspect

from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now


@python_2_unicode_compatible
class TaskType(object):
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.__class__._registry[name] = self

    def __str__(self):
        return force_text(self.label)


@python_2_unicode_compatible
class Task(object):
    def __init__(self, task_type, kwargs):
        self.task_type = task_type
        self.kwargs = kwargs

    def __str__(self):
        return force_text(self.task_type)

    def get_time_started(self):
        time_start = self.kwargs.get('time_start')
        if time_start:
            return now() - timedelta(seconds=monotonic() - self.kwargs['time_start'])
        else:
            return None


@python_2_unicode_compatible
class CeleryQueue(object):
    _registry = {}
    _inspect_instance = inspect()

    @classmethod
    def all(cls):
        return sorted(
            cls._registry.values(), key=lambda instance: instance.label
        )

    @classmethod
    def get(cls, queue_name):
        return cls._registry[queue_name]

    def __init__(self, name, label, is_default_queue=False, transient=False):
        self.name = name
        self.label = label
        self.is_default_queue = is_default_queue
        self.is_transient = transient
        self.task_types = []
        self.__class__._registry[name] = self

    def __str__(self):
        return force_text(self.label)

    def add_task_type(self, *args, **kwargs):
        self.task_types.append(TaskType(*args, **kwargs))

    def get_active_tasks(self):
        return self._process_task_dictionary(
            task_dictionary=self.__class__._inspect_instance.active()
        )

    def get_reserved_tasks(self):
        return self._process_task_dictionary(
            task_dictionary=self.__class__._inspect_instance.reserved()
        )

    def get_scheduled_tasks(self):
        return self._process_task_dictionary(
            task_dictionary=self.__class__._inspect_instance.scheduled()
        )

    def _process_task_dictionary(self, task_dictionary):
        result = []
        for worker, tasks in task_dictionary.items():
            for task in tasks:
                if task['delivery_info']['routing_key'] == self.name:
                    task_type = TaskType.get(name=task['name'])
                    result.append(Task(task_type=task_type, kwargs=task))

        return result
