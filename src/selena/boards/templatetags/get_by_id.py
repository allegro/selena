#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import template


register = template.Library()


@register.filter
def get_by_id(items, item_id):
    for item in items:
        if item.pk == item_id:
            return item.name
    return "" if not item_id else "ID#%s" % item_id
