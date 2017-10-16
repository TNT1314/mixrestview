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

from django.forms import Form
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

__all__ = ['ViewForm']


class ViewForm(Form):
    """
        overload add_error function
    """

    def add_error(self, field, error):
        """
            Update the content of `self._errors`.

            The `field` argument is the name of the field to which the errors
            should be added. If its value is None the errors will be treated as
            NON_FIELD_ERRORS.

            The `error` argument can be a single error, a list of errors, or a
            dictionary that maps field names to lists of errors. What we define as
            an "error" can be either a simple string or an instance of
            ValidationError with its message attribute set and what we define as
            list or dictionary can be an actual `list` or `dict` or an instance
            of ValidationError with its `error_list` or `error_dict` attribute set.

            If `error` is a dictionary, the `field` argument *must* be None and
            errors will be added to the fields that correspond to the keys of the
            dictionary.
        """
        if not isinstance(error, ValidationError):
            # Normalize to ValidationError and let its constructor
            # do the hard work of making sense of the input.
            error = ValidationError(error)

        if hasattr(error, 'error_dict'):
            if field is not None:
                raise TypeError(
                    "The argument `field` must be `None` when the `error` "
                    "argument contains errors for multiple fields."
                )
            else:
                error = error.error_dict
        else:
            error = {field or NON_FIELD_ERRORS: error.error_list}

        for field, error_list in error.items():
            if field not in self.errors:
                if field != NON_FIELD_ERRORS and field not in self.fields:
                    raise ValueError(
                        "'%s' has no field named '%s'." % (self.__class__.__name__, field))
                if field == NON_FIELD_ERRORS:
                    self._errors[field] = self.error_class(error_class='nonfield')
                else:
                    self._errors[field] = self.error_class()

            error_help = self.fields.get(field).help_text if field else "Nothing Help."
            error_mesg = [u'!error: {}'.format(err.message) for err in error_list]
            error_mesg.append(u'?helps: {}'.format(error_help))

            error_back = [ValidationError(err) for err in error_mesg]
            self._errors[field].extend(error_back)

            if field in self.cleaned_data:
                del self.cleaned_data[field]
