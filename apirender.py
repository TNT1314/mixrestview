#! usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

""" 
    auth: wormer@wormer.cn
    proj: site_salary
    date: 2017-10-13
    desc: 
        site_salary
"""

from datetime import datetime

import fields
from rest_framework.renderers import BrowsableAPIRenderer


class WebApiRenderer(BrowsableAPIRenderer):
    """
        overload restFramework renderer
    """

    template = 'webapi.html'

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super(WebApiRenderer, self).get_context(data, accepted_media_type, renderer_context)

        # 获取帮助信息
        param_help_text = self.get_params_help(renderer_context['view'])

        context.update({"helps":param_help_text})

        return context

    def get_params_help(self, view):
        """
            this function to get param help_text
            :param view:
            :return:
        """
        help_list = list()
        feilds = view._meta.param_fields
        for f_name in feilds:
            f_item = feilds.get(f_name)
            helps_dict = dict()
            helps_dict["name"] = f_name
            helps_dict["type"] = f_item.type_name
            helps_dict["need"] = u"是" if f_item.required else u"否"
            helps_dict["desc"] = f_item.help_text

            if isinstance(f_item, fields.RegexField):
                helps_dict["demo"] = "xx={}  ".format(f_item.regex.regex.pattern)
            elif isinstance(f_item, fields.BooleanField):
                helps_dict["demo"] = "xx=0  <0:False,1:True>".format(f_item.help_text)
            elif isinstance(f_item, fields.CharField):
                helps_dict["demo"] = "xx=Hello  "
            elif isinstance(f_item, fields.IntegerField):
                helps_dict["demo"] = "xx=1024  <min:{} max:{}>".format(
                    f_item.min_value if f_item.min_value else "(sys int min)",
                    f_item.max_value if f_item.max_value else "(sys int max)")
            elif isinstance(f_item, fields.FloatField):
                helps_dict["demo"] = "xx=3.1415926  <min:{} max:{}>".format(
                    f_item.min_value if f_item.min_value else "(sys float min)",
                    f_item.max_value if f_item.max_value else "(sys float max)")
            elif isinstance(f_item, fields.DecimalField):
                places = f_item.decimal_places if f_item.decimal_places else 6
                digits = f_item.max_digits if f_item.max_digits else 4
                helps_dict["demo"] = "xx={}.{}  <min:{} max:{} places:{} digits:{}>".format(
                    '3'*(places-digits),
                    '5' * digits,
                    f_item.min_value if f_item.min_value else "(sys float min)",
                    f_item.max_value if f_item.max_value else "(sys float max)",
                    places,
                    digits,
                )
            elif isinstance(f_item, fields.ImageField):
                helps_dict["demo"] = "HTTP POST <binary>"
            elif isinstance(f_item, fields.DateField):
                helps_dict["demo"] = "xx={}  <date>".format(datetime.now().strftime("%Y-%m-%d"))
            else:
                helps_dict["demo"] = u"无示例"

            help_list.append(helps_dict)
        return help_list

