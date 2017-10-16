#! usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

""" 
    date: 2017-10-12
    desc: View utils package
"""

from datetime import datetime
from django.conf.urls import url
from django.core.urlresolvers import RegexURLPattern


def split_camel_name(name, fall=False):
    """
        Split camel formated names:

        GenerateURLs => [Generate, URLs]
        generateURLsLite => [generate, URLs, Lite]
    """
    if not name:
        return []

    lastest_upper = name[0].isupper()
    idx_list = []
    for idx, char in enumerate(name):
        upper = char.isupper()
        # rising
        if upper and not lastest_upper:
            idx_list.append(idx)
        # falling
        elif fall and not upper and lastest_upper:
            idx_list.append(idx-1)
        lastest_upper = upper

    l_idx = 0
    name_items = []
    for r_idx in idx_list:
        name_items.append(name[l_idx:r_idx])
        l_idx = r_idx
    name_items.append(name[l_idx:])

    return name_items


def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list


def camel2path(name):
    """
        GenerateURLs => generate/urls
    """
    return '/'.join(split_camel_name(name)).lower() + '/'


def timestamp2datetime(timestamp):
    return datetime.fromtimestamp(timestamp)
 
