#! usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

""" 
    date: 2017-10-13
"""

import re

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class ValidateMixin(object):
    """
        Extend Validator a method 'is_valid'
    """

    def is_valid(self, value):
        try:
            self(value)
            return True
        except ValidationError:
            return False


class RegexPlus(ValidateMixin, RegexValidator):
    pass


# 数字判断
valid_int = RegexPlus(re.compile('^\+?[1-9][0-9]*$'), '验证是否为数字！')
# 手机验证
valid_mobile = RegexPlus(re.compile('^1[0-9]{10}$'), '手机号格式不正确！')
# 中文验证
valid_chinese = RegexPlus(re.compile('^[\u4e00-\u9fa5]*$'), '含有非中文字符！')
# 邮箱判断
valid_email = RegexPlus(re.compile('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'), '邮箱格式不正确！')
# 社会信用代码
valid_social= RegexPlus(re.compile('^[1-9A-GY]{1}[1239]{1}[1-5]{1}[0-9]{5}[0-9A-Z]{10}$'), '公司统一信用代码不正确！')
# 身份证号
valid_identity = RegexPlus(re.compile(
        '^[1-9]\d{7}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}$|^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$'
    ),
    '身份证格式不正确！'
)




