from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import Index, IndexInstanceNode, IndexTemplateNode


class IndexInstanceNodeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(child=RecursiveField())
    documents_count = serializers.SerializerMethodField()
    documents = serializers.HyperlinkedIdentityField(
        view_name='rest_api:index-node-documents'
    )

    class Meta:
        fields = (
            'documents', 'documents_count', 'children', 'id', 'level', 'parent',
            'value'
        )
        model = IndexInstanceNode

    def get_documents_count(self, instance):
        return instance.documents.count()


class IndexTemplateNodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'enabled', 'expression', 'id', 'index', 'level', 'link_documents',
            'parent'
        )
        model = IndexTemplateNode


class IndexSerializer(serializers.ModelSerializer):
    instance_root = IndexInstanceNodeSerializer(read_only=True)
    node_templates = IndexTemplateNodeSerializer(read_only=True, many=True)

    class Meta:
        fields = (
            'document_types', 'enabled', 'id', 'instance_root', 'label',
            'node_templates',
        )
        model = Index
