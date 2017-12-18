from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from converter.models import Transformation
from rest_framework import generics
from rest_framework.response import Response

from .models import StagingFolderSource
from .serializers import StagingFolderFileSerializer, StagingFolderSerializer


class APIStagingSourceFileView(generics.GenericAPIView):
    """
    Details of the selected staging file.
    """
    serializer_class = StagingFolderFileSerializer

    def get(self, request, staging_folder_pk, encoded_filename):
        staging_folder = get_object_or_404(
            StagingFolderSource, pk=staging_folder_pk
        )
        return Response(
            StagingFolderFileSerializer(
                staging_folder.get_file(encoded_filename=encoded_filename),
                context={'request': request}
            ).data
        )


class APIStagingSourceListView(generics.ListAPIView):
    """
    Returns a list of all the staging folders and the files they contain.
    """

    serializer_class = StagingFolderSerializer
    queryset = StagingFolderSource.objects.all()


class APIStagingSourceView(generics.RetrieveAPIView):
    """
    Details of the selected staging folders and the files it contains.
    """
    serializer_class = StagingFolderSerializer
    queryset = StagingFolderSource.objects.all()


class APIStagingSourceFileImageView(generics.RetrieveAPIView):
    """
    Returns an image representation of the selected document.
    ---
    GET:
        omit_serializer: true
        parameters:
            - name: size
              description: 'x' seprated width and height of the desired image representation.
              paramType: query
              type: number
    """

    def get_serializer_class(self):
        return None

    def retrieve(self, request, *args, **kwargs):
        staging_folder = get_object_or_404(
            StagingFolderSource, pk=self.kwargs['staging_folder_pk']
        )
        staging_file = staging_folder.get_file(
            encoded_filename=self.kwargs['encoded_filename']
        )

        size = request.GET.get('size')

        return HttpResponse(
            staging_file.get_image(
                size=size,
                transformations=Transformation.objects.get_for_model(
                    staging_folder, as_classes=True
                )
            ), content_type='image'
        )
