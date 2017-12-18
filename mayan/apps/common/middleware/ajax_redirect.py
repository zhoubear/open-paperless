from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponseRedirect


class AjaxRedirect(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = getattr(
                    settings, 'AJAX_REDIRECT_CODE', 302
                )
        return response
