#! usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

""" 
    date: 2017-10-12
    desc: new api view, mix django form and restframework view
"""

from rest_framework.response import Response

from .mixview import View


class APIView(View):
    """
        base apiview for client api
    """

    def get_view_name(self):
        if hasattr(self, 'name'):
            return self.name
        return super(APIView, self).get_view_name()

    def view(self, request, *args, **kwargs):
        if self.logger:
            self.logger.info("m=%s g=%s p=%s u=%s",
                request.META, request.query_params, request.data, request.user, extra=None)
        context = self.get_context(request, *args, **kwargs)
        return Response(context)

    def get(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)

    post = get

    def get_default_context(self):
        return self.get_renderer_context()

    def get_context(request, *args, **kwargs):
        raise NotImplementedError

    def handle_param_errors(self, exc):
        return Response(exc)

    def handle_exception(self, exc):
        if self.logger:
            self.logger.error(exc.message)
        return Response(exc.message)