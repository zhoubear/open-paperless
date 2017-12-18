from __future__ import unicode_literals

from django.utils.encoding import force_text

from rest_framework import serializers
from rest_framework.reverse import reverse

from common.models import SharedUploadedFile

from .models import (
    Document, DocumentVersion, DocumentPage, DocumentType,
    DocumentTypeFilename, RecentDocument
)
from .settings import setting_language
from .tasks import task_upload_new_version


class DocumentPageSerializer(serializers.HyperlinkedModelSerializer):
    document_version_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ('document_version_url', 'image_url', 'page_number', 'url')
        model = DocumentPage

    def get_document_version_url(self, instance):
        return reverse(
            'rest_api:documentversion-detail', args=(
                instance.document.pk, instance.document_version.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_image_url(self, instance):
        return reverse(
            'rest_api:documentpage-image', args=(
                instance.document.pk, instance.document_version.pk,
                instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:documentpage-detail', args=(
                instance.document.pk, instance.document_version.pk,
                instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )


class DocumentTypeFilenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTypeFilename
        fields = ('filename',)


class DocumentTypeSerializer(serializers.HyperlinkedModelSerializer):
    documents_url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:documenttype-document-list',
    )
    documents_count = serializers.SerializerMethodField()
    filenames = DocumentTypeFilenameSerializer(many=True, read_only=True)

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:documenttype-detail'},
        }
        fields = (
            'delete_time_period', 'delete_time_unit', 'documents_url',
            'documents_count', 'id', 'label', 'filenames', 'trash_time_period',
            'trash_time_unit', 'url'
        )
        model = DocumentType

    def get_documents_count(self, obj):
        return obj.documents.count()


class WritableDocumentTypeSerializer(serializers.ModelSerializer):
    documents_url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:documenttype-document-list',
    )
    documents_count = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:documenttype-detail'},
        }
        fields = (
            'delete_time_period', 'delete_time_unit', 'documents_url',
            'documents_count', 'id', 'label', 'trash_time_period',
            'trash_time_unit', 'url'
        )
        model = DocumentType

    def get_documents_count(self, obj):
        return obj.documents.count()


class DocumentVersionSerializer(serializers.HyperlinkedModelSerializer):
    document_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    pages_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'document': {'view_name': 'rest_api:document-detail'},
            'file': {'use_url': False},
        }
        fields = (
            'checksum', 'comment', 'document_url', 'download_url', 'encoding',
            'file', 'mimetype', 'pages_url', 'size', 'timestamp', 'url'
        )
        model = DocumentVersion
        read_only_fields = ('document', 'file', 'size')

    def get_size(self, instance):
        return instance.size

    def get_document_url(self, instance):
        return reverse(
            'rest_api:document-detail', args=(
                instance.document.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_download_url(self, instance):
        return reverse(
            'rest_api:documentversion-download', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_pages_url(self, instance):
        return reverse(
            'rest_api:documentversion-page-list', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:documentversion-detail', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )


class WritableDocumentVersionSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    pages_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'file': {'use_url': False},
        }
        fields = (
            'checksum', 'comment', 'document_url', 'download_url', 'encoding',
            'file', 'mimetype', 'pages_url', 'timestamp', 'url'
        )
        model = DocumentVersion
        read_only_fields = ('document', 'file')

    def get_document_url(self, instance):
        return reverse(
            'rest_api:document-detail', args=(
                instance.document.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_download_url(self, instance):
        return reverse(
            'rest_api:documentversion-download', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_pages_url(self, instance):
        return reverse(
            'rest_api:documentversion-page-list', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:documentversion-detail', args=(
                instance.document.pk, instance.pk,
            ), request=self.context['request'], format=self.context['format']
        )


class NewDocumentVersionSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True)
    file = serializers.FileField(use_url=False)

    def save(self, document, _user):
        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=self.validated_data['file']
        )

        task_upload_new_version.delay(
            comment=self.validated_data.get('comment', ''),
            document_id=document.pk,
            shared_uploaded_file_id=shared_uploaded_file.pk, user_id=_user.pk
        )


class DeletedDocumentSerializer(serializers.HyperlinkedModelSerializer):
    document_type_label = serializers.SerializerMethodField()
    restore = serializers.HyperlinkedIdentityField(
        view_name='rest_api:trasheddocument-restore'
    )

    class Meta:
        extra_kwargs = {
            'document_type': {'view_name': 'rest_api:documenttype-detail'},
            'url': {'view_name': 'rest_api:trasheddocument-detail'}
        }
        fields = (
            'date_added', 'deleted_date_time', 'description', 'document_type',
            'document_type_label', 'id', 'label', 'language', 'restore',
            'url', 'uuid',
        )
        model = Document
        read_only_fields = (
            'deleted_date_time', 'description', 'document_type', 'label',
            'language'
        )

    def get_document_type_label(self, instance):
        return instance.document_type.label


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    document_type = DocumentTypeSerializer()
    latest_version = DocumentVersionSerializer(many=False, read_only=True)
    versions_url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:document-version-list',
    )

    class Meta:
        extra_kwargs = {
            'document_type': {'view_name': 'rest_api:documenttype-detail'},
            'url': {'view_name': 'rest_api:document-detail'}
        }
        fields = (
            'date_added', 'description', 'document_type', 'id', 'label',
            'language', 'latest_version', 'url', 'uuid', 'versions_url',
        )
        model = Document
        read_only_fields = ('document_type',)


class WritableDocumentSerializer(serializers.ModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    latest_version = DocumentVersionSerializer(many=False, read_only=True)
    versions = serializers.HyperlinkedIdentityField(
        view_name='rest_api:document-version-list',
    )
    url = serializers.HyperlinkedIdentityField(
        view_name='rest_api:document-detail',
    )

    class Meta:
        fields = (
            'date_added', 'description', 'document_type', 'id', 'label',
            'language', 'latest_version', 'url', 'uuid', 'versions',
        )
        model = Document
        read_only_fields = ('document_type',)


class NewDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    def save(self, _user):
        document = Document.objects.create(
            description=self.validated_data.get('description', ''),
            document_type=self.validated_data['document_type'],
            label=self.validated_data.get(
                'label', force_text(self.validated_data['file'])
            ),
            language=self.validated_data.get(
                'language', setting_language.value
            )
        )
        document.save(_user=_user)

        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=self.validated_data['file']
        )

        task_upload_new_version.delay(
            document_id=document.pk,
            shared_uploaded_file_id=shared_uploaded_file.pk, user_id=_user.pk
        )

        self.instance = document
        return document

    class Meta:
        fields = (
            'description', 'document_type', 'id', 'file', 'label', 'language',
        )
        model = Document


class RecentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('document', 'datetime_accessed')
        model = RecentDocument
