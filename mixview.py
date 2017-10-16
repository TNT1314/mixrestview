#! usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
""" 
    date: 2017-10-12
    desc: metaclass
"""

from urlparse import urljoin
from collections import OrderedDict

from django import forms
from django.utils.six import with_metaclass

from rest_framework.views import APIView
from rest_framework.response import Response

from .param import Param
from .apiform import ViewForm
from .utils import camel2path


class ViewOptions(object):
    """
        View options class

        * name              resolver name of the URL patterns, default is view name
        * path              URL related path generation from parents
        * param_managed     whether manage parameters before dispatching to handler
        * param_fields      parameter's name and field pairs definition,
                            this attribute will generate all parents' param_fields
        * param_dependency  dependency between parameters,
                            format as (name, ((field, [(name, field), ...]), ...))
        * form              form class used to manage parameters
        * decorators        view's decorators generate with the nearest-first logic,
                            this attribute will generate all parents' decorators
    """

    def __init__(self, options=None, parent=None):
        self.view = None
        self.children = []

        self.name = getattr(options, 'name', '')
        self.decorators = list(reversed(getattr(options, 'decorators', ())))

        if parent:
            p_opts = parent._meta
            self.parent = parent
            self.path = getattr(options, 'path', None)
            self.form = getattr(options, 'form', p_opts.form)
            self.param_managed = getattr(options, 'param_managed', p_opts.param_managed)
            self.param_fields = p_opts.param_fields.copy()
            self.param_dependency = p_opts.param_dependency.copy()
            self.param_fields.update(getattr(options, 'param_fields', ()))
            self.param_dependency.update(getattr(options, 'param_dependency', ()))
            self.decorators.extend(p_opts.decorators)
        else:
            self.path = getattr(options, 'path', '/')
            self.parent = None
            self.form = getattr(options, 'form', ViewForm)
            self.param_fields = OrderedDict(getattr(options, 'param_fields', ()))
            self.param_dependency = OrderedDict(getattr(options, 'param_dependency', ()))
            self.param_managed = getattr(options, 'param_managed', True)

    def contribute_to_class(self, cls, name):
        self.view = cls

        if not self.name:
            self.name = self.view.__name__
        if self.path is None:
            self.path = urljoin(self.parent._meta.path, camel2path(self.name))
        if self.parent:
            self.parent._meta.children.append(cls)

        form_attrs = dict(self.param_fields)
        form_attrs['__module__'] = cls.__module__
        cls.param_form = type(self.form)(cls.__name__ + b'Form', (self.form, ), form_attrs)

        setattr(cls, name, self)

    def decorate_handler(self, handler):
        for decorator in self.decorators:
            handler = decorator(handler)
        return handler


class ViewMetaclass(type):
    """
        Metaclass of the view classes
    """

    def __new__(mcs, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ViewMetaclass)]
        assert len(parents) <= 1
        __name__ = attrs.pop('__name__', name)
        new_cls = super(ViewMetaclass, mcs).__new__(mcs, name, bases, attrs)
        option_class = getattr(new_cls, 'option_class', ViewOptions)
        if parents:
            opts = option_class(attrs.pop('Meta', None), parents[0])
        else:
            opts = option_class(attrs.pop('Meta', None))
        opts.contribute_to_class(new_cls, '_meta')
        new_cls.__name__ = __name__
        return new_cls


class APIViewOptions(ViewOptions):
    """
        APIView options class
        Extend options:
        * wrappers          view's wrappers generate with the nearest-first logic,
                            this attribute will generate all parents' wrappers
    """

    def __init__(self, options=None, parent=None):
        super(APIViewOptions, self).__init__(options, parent)
        self.wrappers = list(reversed(getattr(options, 'wrappers', ())))

        if self.parent:
            self.wrappers.extend(parent._meta.wrappers)

    def wrap_view(self, view):
        for wrapper in self.wrappers:
            view = wrapper(view)
        return view


class View(with_metaclass(ViewMetaclass, APIView)):
    """
        Rest-Framework compatible view
    """

    option_class = APIViewOptions

    def get_renderer_context(self):
        context = super(View, self).get_renderer_context()
        context.update({'view_options': self._meta,})
        return context

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        ___ = request.body

        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)

            handler_name = request.method.lower()
            if handler_name in self.http_method_names:

                if hasattr(self, handler_name):
                    handler = getattr(self, handler_name)
                    if not getattr(handler, '_decorated', False):
                        decorated_handler = self._meta.decorate_handler(handler)
                        if decorated_handler is not handler:
                            decorated_handler.__dict__['_decorated'] = True
                            setattr(self, handler_name, decorated_handler)
                            handler = decorated_handler
                else:
                    handler = self.http_method_not_allowed

                request.params = Param(self, request, method=handler_name)
                request._request.params = request.params
                response = handler(request, *args, **kwargs)
            else:
                handler = self.http_method_not_allowed
                response = handler(request, *args, **kwargs)
        except forms.ValidationError, exc:
            response = self.handle_param_errors(exc)
        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    def handle_param_errors(self, exc):
        if hasattr(exc, 'error_dict'):
            return Response(exc.error_dict, status=400)
        else:
            return Response({'*': exc}, status=400)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(View, cls).as_view(*args, **kwargs)
        return cls._meta.wrap_view(view)
