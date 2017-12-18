from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from documents.models import DocumentType
from documents.serializers import DocumentSerializer, DocumentTypeSerializer

from .models import SmartLink, SmartLinkCondition


class SmartLinkConditionSerializer(serializers.HyperlinkedModelSerializer):
    smart_link_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'enabled', 'expression', 'foreign_document_data', 'inclusion',
            'id', 'negated', 'operator', 'smart_link_url', 'url'
        )
        model = SmartLinkCondition

    def create(self, validated_data):
        validated_data['smart_link'] = self.context['smart_link']
        return super(SmartLinkConditionSerializer, self).create(validated_data)

    def get_smart_link_url(self, instance):
        return reverse(
            'rest_api:smartlink-detail', args=(instance.smart_link.pk,),
            request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:smartlinkcondition-detail', args=(
                instance.smart_link.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )


class SmartLinkSerializer(serializers.HyperlinkedModelSerializer):
    conditions_url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:smartlinkcondition-list'
    )
    document_types = DocumentTypeSerializer(read_only=True, many=True)

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:smartlink-detail'},
        }
        fields = (
            'conditions_url', 'document_types', 'dynamic_label', 'enabled',
            'label', 'id', 'url'
        )
        model = SmartLink


class ResolvedSmartLinkDocumentSerializer(DocumentSerializer):
    resolved_smart_link_url = serializers.SerializerMethodField()

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + (
            'resolved_smart_link_url',
        )
        read_only_fields = DocumentSerializer.Meta.fields

    def get_resolved_smart_link_url(self, instance):
        return reverse(
            'rest_api:resolvedsmartlink-detail', args=(
                self.context['document'].pk, self.context['smart_link'].pk
            ), request=self.context['request'],
            format=self.context['format']
        )


class ResolvedSmartLinkSerializer(SmartLinkSerializer):
    resolved_dynamic_label = serializers.SerializerMethodField()
    resolved_smart_link_url = serializers.SerializerMethodField()
    resolved_documents_url = serializers.SerializerMethodField()

    class Meta(SmartLinkSerializer.Meta):
        fields = SmartLinkSerializer.Meta.fields + (
            'resolved_dynamic_label', 'resolved_smart_link_url',
            'resolved_documents_url'
        )
        read_only_fields = SmartLinkSerializer.Meta.fields

    def get_resolved_documents_url(self, instance):
        return reverse(
            'rest_api:resolvedsmartlinkdocument-list',
            args=(self.context['document'].pk, instance.pk,),
            request=self.context['request'], format=self.context['format']
        )

    def get_resolved_dynamic_label(self, instance):
        return instance.get_dynamic_label(document=self.context['document'])

    def get_resolved_smart_link_url(self, instance):
        return reverse(
            'rest_api:resolvedsmartlink-detail',
            args=(self.context['document'].pk, instance.pk,),
            request=self.context['request'], format=self.context['format']
        )


class WritableSmartLinkSerializer(serializers.ModelSerializer):
    conditions_url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:smartlinkcondition-list'
    )
    document_types_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document type primary keys to which this '
            'smart link will be attached.'
        ), required=False
    )

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:smartlink-detail'},
        }
        fields = (
            'conditions_url', 'document_types_pk_list', 'dynamic_label',
            'enabled', 'label', 'id', 'url'
        )
        model = SmartLink

    def validate(self, attrs):
        document_types_pk_list = attrs.pop('document_types_pk_list', None)
        document_types_result = []

        if document_types_pk_list:
            for pk in document_types_pk_list.split(','):
                try:
                    document_type = DocumentType.objects.get(pk=pk)
                except DocumentType.DoesNotExist:
                    raise ValidationError(_('No such document type: %s') % pk)
                else:
                    # Accumulate valid stored document_type pks
                    document_types_result.append(document_type.pk)

        attrs['document_types'] = DocumentType.objects.filter(
            pk__in=document_types_result
        )
        return attrs
