# mixrestview

django restframework api params

1.make sure django and restframework package in your env.


    (env)$PATH: pip install django==1.10.5
    (env)$PATH: pip install djangorestframework==3.5.4


2.install mixrestview.


    (env)$PATH: pip install mixrestview


3.add mixrestview to INSTALLED_APPS.


    INSTALLED_APPS = [
        ......
        'rest_framework',
        'mixrestview',
    ]


4.add django-restframework DEFAULT_RENDERER_CLASSES.


    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'mixrestview.apirender.WebApiRenderer',
            'rest_framework.renderers.JSONRenderer', #option
        ),
    }



sample example:


1.create project:


    (env)$PATH: python django-admin.py startproject test_project


2.create app:


    (env)$PATH: cd test_project
    (env)$PATH: python manage.py startapp webapi


3.add views directory:
    (env)$PATH: cd webapi
    (env)$PATH: mkdir apis
    (env)$PATH: vi apis/rest_view_test.py



4.add url to project
    urlpatterns = [
        # api
        url(r'^api/', include('webapi.urls', namespace='webapi')),
    ]



5.add url to app
    urlpatterns = [
        url(r'^test/', include('webapi.apis.rest_view_test')),
    ]



6.run server:
    (env)$PATH:python manage.py runserver:8000



7.browse the address in your browser:
    http://localhost:8000/api/test/ping



note:

    a.rest_view_test.py:

        #! usr/bin/env python
        # encoding: utf-8
        """
            auth: your name
            date: now date
        """

        from mixrestview import ViewSite, fields, validators, APIView


        site = ViewSite(name="test",app_name="webapi")


        @site
        class AppPing(APIView):
            """
                discription of Interface
            """

            def get_context(request, *args, **kwargs):

                result = dict()
                result['code'] = '10000'
                result['mesg'] = 'success'
                return result

            class Meta:
                path = 'ping'
                param_fields = (
                    ('char', fields.CharField(required=True, help_text=u"char")),
                    ('int', fields.IntegerField(required=True, help_text=u"int")),
                    ('boolean', fields.BooleanField(required=True, help_text=u"boolean")),
                    ('float', fields.FloatField(required=True, help_text=u"float")),
                    ('date', fields.DateField(required=True, help_text=u"date")),
                    ('image', fields.ImageField(required=True, help_text=u"image")),
                    ('deciminal', fields.DecimalField(required=True, max_digits=4, decimal_places=10, help_text=u"deciminal")),
                    ('regex', fields.RegexField(required=True, regex=validators.valid_identity, help_text=u"regex")),
                )

        urlpatterns = site.urlpatterns
