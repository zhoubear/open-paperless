from __future__ import unicode_literals

from django.db import connection, transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings

from rest_framework_recursive.fields import RecursiveField

from documents.models import Document
from documents.serializers import DocumentSerializer

from .models import Cabinet


class CabinetSerializer(serializers.ModelSerializer):
    children = RecursiveField(
        help_text=_('List of children cabinets.'), many=True, read_only=True
    )
    documents_count = serializers.SerializerMethodField(
        help_text=_('Number of documents on this cabinet level.')
    )
    full_path = serializers.SerializerMethodField(
        help_text=_(
            'The name of this cabinet level appended to the names of its '
            'ancestors.'
        )
    )
    documents_url = serializers.HyperlinkedIdentityField(
        help_text=_(
            'URL of the API endpoint showing the list documents inside this '
            'cabinet.'
        ), view_name='rest_api:cabinet-document-list'
    )
    parent_url = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:cabinet-detail'},
        }
        fields = (
            'children', 'documents_count', 'documents_url', 'full_path', 'id',
            'label', 'parent', 'parent_url', 'url'
        )
        model = Cabinet

    def get_documents_count(self, obj):
        return obj.get_document_count(user=self.context['request'].user)

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_parent_url(self, obj):
        if obj.parent:
            return reverse(
                'rest_api:cabinet-detail', args=(obj.parent.pk,),
                format=self.context['format'],
                request=self.context.get('request')
            )
        else:
            return ''


class WritableCabinetSerializer(serializers.ModelSerializer):
    documents_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys to add to this '
            'cabinet.'
        ), required=False
    )

    # This is here because parent is optional in the model but the serializer
    # sets it as required.
    parent = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Cabinet.objects.all(), required=False
    )

    class Meta:
        fields = ('documents_pk_list', 'label', 'id', 'parent')
        model = Cabinet

    def _add_documents(self, documents_pk_list, instance):
        instance.documents.add(
            *Document.objects.filter(pk__in=documents_pk_list.split(','))
        )

    def create(self, validated_data):
        documents_pk_list = validated_data.pop('documents_pk_list', '')

        instance = super(WritableCabinetSerializer, self).create(validated_data)

        if documents_pk_list:
            self._add_documents(
                documents_pk_list=documents_pk_list, instance=instance
            )

        return instance

    def update(self, instance, validated_data):
        documents_pk_list = validated_data.pop('documents_pk_list', '')

        instance = super(WritableCabinetSerializer, self).update(
            instance, validated_data
        )

        if documents_pk_list:
            instance.documents.clear()
            self._add_documents(
                documents_pk_list=documents_pk_list, instance=instance
            )

        return instance

    def run_validation(self, data=None):
        # Copy data into a new dictionary since data is an immutable type
        result = data.copy()

        # Add None parent to keep validation from failing.
        # This is here because parent is optional in the model but the serializer
        # sets it as required.
        result.setdefault('parent')

        data = super(WritableCabinetSerializer, self).run_validation(result)

        # Explicit validation of uniqueness of parent+label as the provided
        # unique_together check in Meta is not working for all 100% cases
        # when there is a FK in the unique_together tuple
        # https://code.djangoproject.com/ticket/1751
        with transaction.atomic():
            if connection.vendor == 'oracle':
                queryset = Cabinet.objects.filter(parent=data['parent'], label=data['label'])
            else:
                queryset = Cabinet.objects.select_for_update().filter(parent=data['parent'], label=data['label'])

            if queryset.exists():
                params = {
                    'model_name': _('Cabinet'),
                    'field_labels': _('Parent and Label')
                }
                raise serializers.ValidationError(
                    {
                        api_settings.NON_FIELD_ERRORS_KEY: [
                            _(
                                '%(model_name)s with this %(field_labels)s '
                                'already exists.'
                            ) % params
                        ],
                    },
                )

        return data


class CabinetDocumentSerializer(DocumentSerializer):
    cabinet_document_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to a document in relation to the cabinet '
            'storing it. This URL is different than the canonical document '
            'URL.'
        )
    )

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ('cabinet_document_url',)
        read_only_fields = DocumentSerializer.Meta.fields

    def get_cabinet_document_url(self, instance):
        return reverse(
            'rest_api:cabinet-document', args=(
                self.context['cabinet'].pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )


class NewCabinetDocumentSerializer(serializers.Serializer):
    documents_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys to add to this '
            'cabinet.'
        )
    )

    def _add_documents(self, documents_pk_list, instance):
        instance.documents.add(
            *Document.objects.filter(pk__in=documents_pk_list.split(','))
        )

    def create(self, validated_data):
        documents_pk_list = validated_data['documents_pk_list']

        if documents_pk_list:
            self._add_documents(
                documents_pk_list=documents_pk_list,
                instance=validated_data['cabinet']
            )

        return {'documents_pk_list': documents_pk_list}
