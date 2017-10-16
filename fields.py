#! usr/bin/env python
# encoding: utf-8

"""
Wrap django form fields to use `default` instead of `required`
"""

from __future__ import unicode_literals, absolute_import

from functools import wraps
from django.db import models
from django.forms import fields
# to prevent Importation-Examination
from django.forms.fields import *
from django.forms.models import fields_for_model
from django.core.exceptions import ValidationError
from django.utils.six import string_types
from django.utils.translation import ugettext_lazy as _


from .validators import valid_mobile
from .utils import timestamp2datetime
from .widgets import BooleanInput, NullBooleanSelect

class _Empty(object):
    def __nonzero__(self):
        return False

    def __str__(self):
        return '<empty>'

empty = _Empty()


def formfield(field, **kwargs):
    kwargs.setdefault('validators', field.validators)
    if isinstance(field, (
            models.AutoField,
            models.PositiveIntegerField,
            models.PositiveSmallIntegerField)):
        return IntegerField(min_value=0, **kwargs)
    else:
        return globals().get(field.get_internal_type(), CharField)(**kwargs)


def field_for_model(
        model, field,
        widget=None, localize=None,
        help_text=None, error_messages=None):
    return fields_for_model(
            model, [field], None,
            widget and {field: widget}, formfield, 
            localize is not None and {field: localize} or localize, None,
            help_text and {field: help_text},
            error_messages and {field: error_messages})[field]


def smart_help_text(field):
    if field.help_text:
        return field.help_text

    if isinstance(field, (fields.BooleanField, fields.NullBooleanField)):
        return '0, false; 1, true'

    if hasattr(field, 'choices'):
        return '; '.join([': '.join(map(unicode, choice)) for choice in field.choices])
    help_text_li = []
    for att in ['max_value', 'min_value', 'max_length', 'min_length']:
        val = getattr(field, att, None)
        if val is not None:
            help_text_li.append('%s: %s' % (att[:3], val))
    return '; '.join(help_text_li)


def wrap_field(fieldclass):
    init_method = fieldclass.__init__

    @wraps(init_method)
    def __init__(self, *args, **kwargs):
        if type(self).__name__ not in fields.__all__[1:]:
            self.type_name = kwargs.pop('type_name', type(self).__bases__)
        else:
            self.type_name = kwargs.pop('type_name', type(self).__name__)
        self.omit = kwargs.pop('omit', empty)
        self.default = kwargs.pop('default', empty)
        if self.omit is not empty:
            kwargs['required'] = False
        elif self.default is not empty:
            kwargs.setdefault('required', True)
        init_method(self, *args, **kwargs)
        self.help_text = smart_help_text(self)

    to_python_method = fieldclass.to_python

    @wraps(to_python_method)
    def to_python(self, value):
        if (value in self.empty_values and self.omit is not empty):
            if callable(self.omit):
                return self.omit()
            return self.omit
        value = to_python_method(self, value)
        return value

    clean_method = fieldclass.clean

    @wraps(clean_method)
    def clean(self, *args, **kwargs):
        try:
            return clean_method(self, *args, **kwargs)
        except ValidationError:
            if self.default is not empty:
                if callable(self.default):
                    return self.default()
                return self.default
            raise

    attrs = {
        '__init__': __init__,
        'to_python': to_python,
        'clean': clean,
    }
    return type(fieldclass)(fieldclass.__name__, (fieldclass, ), attrs)


for _fieldclass_name in fields.__all__[1:]:
    exec '{0} = wrap_field(fields.{0})'.format(_fieldclass_name)


del _fieldclass_name


# overwrite BooleanField and NullBooleanField to accept 0,1
class BooleanField(BooleanField):

    widget = BooleanInput

    def to_python(self, value):
        if isinstance(value, string_types) and value.lower() in ('false', '0'):
            value = False
        elif isinstance(value, string_types) and value.lower() in ('true', '1'):
            value = True
        else:
            value = value
        return value

    def validate(self, value):
        if self.required:
            if not isinstance(value, bool):
                raise ValidationError(self.error_messages['required'], code='required')


class NullBooleanField(NullBooleanField):
    widget = NullBooleanSelect


class MobileField(CharField):
    default_validators = [valid_mobile]


class LongitudeField(FloatField):
    def __init__(self, max_value=180.0, min_value=-180.0, *args, **kwargs):
        super(LongitudeField, self).__init__(
            max_value, min_value, *args, **kwargs)


class LatitudeField(FloatField):
    def __init__(self, max_value=90.0, min_value=-90.0, *args, **kwargs):
        super(LatitudeField, self).__init__(
            max_value, min_value, *args, **kwargs)


class SplitCharField(CharField):
    """
        Split string value with given sep or seps
    """

    default_field = CharField()

    def __init__(self, *args, **kwargs):
        self.sep = kwargs.pop('sep', ',')
        self.field = kwargs.pop('field', self.default_field)
        super(SplitCharField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(SplitCharField, self).clean(value)
        if value:
            return map(self.field.clean, value.split(self.sep))
        else:
            return []


class TimestampField(IntegerField):
    def to_python(self, value):
        v = super(TimestampField, self).to_python(value)
        if v is None:
            return None
        return timestamp2datetime(v)


class PairCharField(CharField):
    """
        Split string value with given seps
    """
    default_error_messages = {
        'invalid': _('Enter a valid value.'),
        'unpaired': _('Enter a valid value.'),
    }

    default_field = (CharField(), CharField())

    def __init__(self, *args, **kwargs):
        self.seps = kwargs.pop('seps', ('|', '.'))
        self.fields = kwargs.pop('fields', self.default_field)
        super(PairCharField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(PairCharField, self).clean(value)
        if value:
            value_list = []
            for val0, val1 in self.gen_split(value):
                value_list.append((self.fields[0].clean(val0), self.fields[1].clean(val1)))
            return value_list
        else:
            return []

    def gen_split(self, value, idx=0):
        if not value:
            return 
        if idx == len(self.seps) - 1:
            pair = value.split(self.seps[idx])
            if len(pair) != 2:
                raise ValidationError(
                        self.error_messages['unpaired'],
                        code='unpaired',
                        params={'seps': self.seps},
                    )
            yield value.split(self.seps[idx])
        else:
            for item in value.split(self.seps[idx]):
                for ret in self.gen_split(item, idx + 1):
                    yield ret


class RegexField(CharField):
    """
        overloadRegexField
    """

    def __init__(self, regex, max_length=None, min_length=None, *args, **kwargs):
        kwargs.setdefault('strip', False)
        super(RegexField, self).__init__(max_length, min_length, *args, **kwargs)
        self._set_regex(regex)
        self.default_error_messages = {
            'invalid': _(regex.message),
            'unpaired': _(regex.message),
        }

    def _get_regex(self):
        return self._regex_validator

    def _set_regex(self, regex):
        self._regex = regex.regex
        self._regex_validator = regex
        self.validators.append(self._regex_validator)

    regex = property(_get_regex, _set_regex)