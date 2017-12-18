from __future__ import absolute_import, unicode_literals

import datetime
import logging
import re

from django.apps import apps
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _


from .settings import setting_limit

logger = logging.getLogger(__name__)


class SearchModel(object):
    registry = {}

    @classmethod
    def get(cls, full_name):
        try:
            result = cls.registry[full_name]
        except KeyError:
            raise KeyError(_('No search model matching the query'))
        if not hasattr(result, 'serializer'):
            result.serializer = import_string(result.serializer_string)

        return result

    @classmethod
    def as_choices(cls):
        return cls.registry

    @classmethod
    def all(cls):
        return cls.registry.values()

    def __init__(self, app_label, model_name, serializer_string, label=None, permission=None):
        self.app_label = app_label
        self.model_name = model_name
        self.search_fields = []
        self._model = None  # Lazy
        self._label = label
        self.serializer_string = serializer_string
        self.permission = permission
        self.__class__.registry[self.get_full_name()] = self

    @property
    def pk(self):
        return self.get_full_name()

    @property
    def model(self):
        if not self._model:
            self._model = apps.get_model(self.app_label, self.model_name)
        return self._model

    @property
    def label(self):
        if not self._label:
            self._label = self.model._meta.verbose_name
        return self._label

    def add_model_field(self, *args, **kwargs):
        """
        Add a search field that directly belongs to the parent SearchModel
        """
        search_field = SearchField(self, *args, **kwargs)
        self.search_fields.append(search_field)

    def assemble_query(self, terms, search_fields):
        """
        Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search
        fields.
        """
        queries = []
        for term in terms:
            or_query = None
            for field in search_fields:
                q = Q(**{'%s__%s' % (field, 'icontains'): term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q

            queries.append(or_query)
        return queries

    def get_all_search_fields(self):
        return self.search_fields

    def get_full_name(self):
        return '%s.%s' % (self.app_label, self.model_name)

    def get_fields_simple_list(self):
        """
        Returns a list of the fields for the SearchModel
        """
        result = []
        for search_field in self.get_all_search_fields():
            result.append((search_field.get_full_name(), search_field.label))

        return result

    def get_search_field(self, full_name):
        try:
            return self.search_fields[full_name]
        except KeyError:
            raise KeyError('No search field named: %s' % full_name)

    def normalize_query(self, query_string,
                        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        """
        Splits the query string in invidual keywords, getting rid of
        unecessary spaces and grouping quoted words together.
        Example:
            >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        """
        return [
            normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)
        ]

    def search(self, query_string, user, global_and_search=False):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        elapsed_time = 0
        start_time = datetime.datetime.now()
        result_set = set()
        search_dict = {}

        if 'q' in query_string:
            # Simple search
            for search_field in self.get_all_search_fields():
                search_dict.setdefault(search_field.get_model(), {
                    'searches': [],
                    'label': search_field.label,
                    'return_value': search_field.return_value
                })
                search_dict[search_field.get_model()]['searches'].append(
                    {
                        'field_name': [search_field.field],
                        'terms': self.normalize_query(
                            query_string.get('q', '').strip()
                        )
                    }
                )
        else:
            for search_field in self.get_all_search_fields():
                if search_field.field in query_string and query_string[search_field.field]:
                    search_dict.setdefault(search_field.get_model(), {
                        'searches': [],
                        'label': search_field.label,
                        'return_value': search_field.return_value
                    })
                    search_dict[search_field.get_model()]['searches'].append(
                        {
                            'field_name': [search_field.field],
                            'terms': self.normalize_query(
                                query_string[search_field.field]
                            )
                        }
                    )

        for model, data in search_dict.items():
            logger.debug('model: %s', model)

            # Initialize per model result set
            model_result_set = set()

            for query_entry in data['searches']:
                # Fashion a list of queries for a field for each term
                field_query_list = self.assemble_query(
                    query_entry['terms'], query_entry['field_name']
                )

                logger.debug('field_query_list: %s', field_query_list)

                # Initialize per field result set
                field_result_set = set()

                # Get results per search field
                for query in field_query_list:
                    logger.debug('query: %s', query)
                    term_query_result_set = set(
                        model.objects.filter(query).values_list(
                            data['return_value'], flat=True
                        )
                    )

                    # Convert the QuerySet to a Python set and perform the
                    # AND operation on the program and not as a query.
                    # This operation ANDs all the field term results
                    # belonging to a single model, making sure to only include
                    # results in the final field result variable if all the
                    # terms are found in a single field.
                    if not field_result_set:
                        field_result_set = term_query_result_set
                    else:
                        field_result_set &= term_query_result_set

                    logger.debug(
                        'term_query_result_set: %s', term_query_result_set
                    )
                    logger.debug('field_result_set: %s', field_result_set)

                if global_and_search:
                    if not model_result_set:
                        model_result_set = field_result_set
                    else:
                        model_result_set &= field_result_set
                else:
                    model_result_set |= field_result_set

            result_set = result_set | model_result_set

        elapsed_time = force_text(
            datetime.datetime.now() - start_time
        ).split(':')[2]

        logger.debug('elapsed_time: %s', elapsed_time)

        queryset = self.model.objects.filter(
            pk__in=list(result_set)[:setting_limit.value]
        )

        if self.permission:
            queryset = AccessControlList.objects.filter_by_access(
                self.permission, user, queryset
            )

        return queryset, result_set, elapsed_time


# SearchField classes
class SearchField(object):
    """
    Search for terms in fields that directly belong to the parent SearchModel
    """
    def __init__(self, search_model, field, label):
        self.search_model = search_model
        self.field = field
        self.label = label
        self.return_value = 'pk'

    def get_full_name(self):
        return self.field

    def get_model(self):
        return self.search_model.model
