from __future__ import unicode_literals

import json

from django.apps import apps
from django.utils.encoding import force_text, python_2_unicode_compatible

from celery.schedules import crontab

from mayan.celery import app


@python_2_unicode_compatible
class StatisticNamespace(object):
    _registry = {}

    @classmethod
    def get_all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, slug):
        return cls._registry[slug]

    def __init__(self, slug, label):
        self.slug = slug
        self.label = label
        self._statistics = []
        self.__class__._registry[slug] = self

    def __str__(self):
        return force_text(self.label)

    def add_statistic(self, *args, **kwargs):
        statistic = Statistic(*args, **kwargs)
        statistic.namespace = self
        self._statistics.append(statistic)

    @property
    def statistics(self):
        return self._statistics


@python_2_unicode_compatible
class Statistic(object):
    _registry = {}

    @staticmethod
    def purge_schedules():
        PeriodicTask = apps.get_model(
            app_label='djcelery', model_name='PeriodicTask'
        )
        StatisticResult = apps.get_model(
            app_label='mayan_statistics', model_name='StatisticResult'
        )

        queryset = PeriodicTask.objects.filter(
            name__startswith='mayan_statistics.'
        ).exclude(name__in=Statistic.get_task_names())

        for periodic_task in queryset:
            crontab_instance = periodic_task.crontab
            periodic_task.delete()

            if crontab_instance and not crontab_instance.periodictask_set.all():
                # Only delete the interval if nobody else is using it
                crontab_instance.delete()

        StatisticResult.objects.filter(
            slug__in=queryset.values_list('name', flat=True)
        ).delete()

    @classmethod
    def get_all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, slug):
        return cls._registry[slug]

    @classmethod
    def get_task_names(cls):
        return [task.get_task_name() for task in cls.get_all()]

    def __init__(self, slug, label, func, renderer, minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'):
        self.slug = slug
        self.label = label
        self.func = func
        self.renderer = renderer

        self.schedule = crontab(
            minute=minute, hour=hour, day_of_week=day_of_week,
            day_of_month=day_of_month, month_of_year=month_of_year,
        )

        app.conf.CELERYBEAT_SCHEDULE.update(
            {
                self.get_task_name(): {
                    'task': 'mayan_statistics.tasks.task_execute_statistic',
                    'schedule': self.schedule,
                    'args': (self.slug,)
                },
            }
        )

        app.conf.CELERY_ROUTES.update(
            {
                self.get_task_name(): {
                    'queue': 'statistics'
                },
            }
        )

        self.__class__._registry[slug] = self

    def __str__(self):
        return force_text(self.label)

    def execute(self):
        self.store_results(results=self.func())

    def get_task_name(self):
        return 'mayan_statistics.task_execute_statistic_{}'.format(self.slug)

    def store_results(self, results):
        from .models import StatisticResult

        StatisticResult.objects.filter(slug=self.slug).delete()

        statistic_result, created = StatisticResult.objects.get_or_create(
            slug=self.slug
        )
        statistic_result.store_data(data=results)

    def get_results(self):
        from .models import StatisticResult

        try:
            return StatisticResult.objects.get(slug=self.slug).get_data()
        except StatisticResult.DoesNotExist:
            return {'series': {}}

    def get_chart_data(self):
        return self.renderer(data=self.get_results()).get_chart_data()


class ChartRenderer(object):
    def __init__(self, data):
        self.data = data

    def get_chart_data(self):
        raise NotImplementedError


class CharJSLine(ChartRenderer):
    template_name = 'statistics/backends/chartjs/line.html'

    dataset_palette = (
        {
            'fillColor': "rgba(220,220,220,0.2)",
            'strokeColor': "rgba(220,220,220,1)",
            'pointColor': "rgba(220,220,220,1)",
            'pointStrokeColor': "#fff",
            'pointHighlightFill': "#fff",
            'pointHighlightStroke': "rgba(220,220,220,1)",
        },
        {
            'fillColor': "rgba(151,187,205,0.2)",
            'strokeColor': "rgba(151,187,205,1)",
            'pointColor': "rgba(151,187,205,1)",
            'pointStrokeColor': "#fff",
            'pointHighlightFill': "#fff",
            'pointHighlightStroke': "rgba(151,187,205,1)",
        },
    )

    def get_chart_data(self):
        labels = []
        datasets = []

        for count, serie in enumerate(self.data['series'].items()):
            series_name, series_data = serie
            dataset_labels = []
            dataset_values = []

            for data_point in series_data:
                dataset_labels.extend(data_point.keys())
                dataset_values.extend(data_point.values())

            labels = dataset_labels
            dataset = {
                'label': series_name,
                'data': dataset_values,
            }
            dataset.update(
                CharJSLine.dataset_palette[
                    count % len(CharJSLine.dataset_palette)
                ]
            )

            datasets.append(dataset)

        data = {
            'labels': labels,
            'datasets': datasets,

        }

        return json.dumps(data)
