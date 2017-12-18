from __future__ import unicode_literals

from rest_framework import renderers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_swagger.views import SwaggerApiView, SwaggerResourcesView


class APIBase(SwaggerResourcesView):
    """
    Main entry point of the API.
    """

    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)


class APIAppView(SwaggerApiView):
    """
    Entry points of the selected app.
    """
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)


class BrowseableObtainAuthToken(ObtainAuthToken):
    """
    Obtain an API authentication token.
    """

    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
