# mixrestview

django restframework api params



# env
1.make sure django and restframework package in your env.


    (env)$PATH: pip install django==1.10.5
    (env)$PATH: pip install djangorestframework==3.5.4



2.install mixrestview.


    (env)$PATH: pip install mixrestview





# sample example:


1.create project:


    (env)$PATH: python django-admin.py startproject test_project



2.create app:


    (env)$PATH: cd test_project
    (env)$PATH: python manage.py startapp webapi



3.update settings(test_project/test_project/settings.py):


    (env)$PATH: vi test_project/settings.py
    
        update:
            INSTALLED_APPS = [
                ......
                'rest_framework',
                'mixrestview',
            ]

            REST_FRAMEWORK = {
                'DEFAULT_RENDERER_CLASSES': (
                    'mixrestview.apirender.WebApiRenderer',
                    'rest_framework.renderers.JSONRenderer', #option
                ),
            }



4.add views directory:


    (env)$PATH: vi urls.py

        update urlpatterns:
            urlpatterns = [
                ......
                url(r'^api/', include('webapi.urls', namespace='webapi')),
            ]

    (env)$PATH: cd webapi
    (env)$PATH: vi urls.py

        insert:
            #! usr/bin/env python
            # encoding: utf-8

            from django.conf.urls import url, include

            urlpatterns = [
                url(r'^test/', include('webapi.apis.rest_view_test')),
            ]

    (env)$PATH: mkdir apis
    (env)$PATH: vi __init__.py
    (env)$PATH: vi apis/rest_view_test.py

        insert:
            #! usr/bin/env python
            # encoding: utf-8
            """
                auth: your name
                date: now date
            """

            from mixrestview import ViewSite, fields, validators, apiview


            site = ViewSite(name="test", app_name="webapi")


            @site
            class AppPing(apiview.APIView):
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
                        ('decimal', fields.DecimalField(required=True, max_digits=4, decimal_places=10, help_text=u"decimal")),
                        ('regex', fields.RegexField(required=True, regex=validators.valid_identity, help_text=u"regex")),
                    )

            urlpatterns = site.urlpatterns



5.run server:


    (env)$PATH:python manage.py runserver:8000



6.browse the address in your browser:


    http://localhost:8000/api/test/ping

