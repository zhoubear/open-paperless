from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.reverse import reverse

from documents.serializers import DocumentSerializer
from user_management.serializers import UserSerializer

from .models import Comment


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    document = DocumentSerializer(read_only=True)
    document_comments_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        fields = (
            'comment', 'document', 'document_comments_url', 'id',
            'submit_date', 'url', 'user'
        )
        model = Comment

    def get_document_comments_url(self, instance):
        return reverse(
            'rest_api:comment-list', args=(
                instance.document.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:comment-detail', args=(
                instance.document.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )


class WritableCommentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    document_comments_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        fields = (
            'comment', 'document', 'document_comments_url', 'id',
            'submit_date', 'url', 'user'
        )
        model = Comment
        read_only_fields = ('document',)

    def create(self, validated_data):
        validated_data['document'] = self.context['document']
        validated_data['user'] = self.context['request'].user
        return super(WritableCommentSerializer, self).create(validated_data)

    def get_document_comments_url(self, instance):
        return reverse(
            'rest_api:comment-list', args=(
                instance.document.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:comment-detail', args=(
                instance.document.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )
