#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.template import loader, Context


class Helper():
    def custom_status_helper(self):
        t = loader.get_template('admin/status_code.html')
        c = Context({})
        rendered = t.render(c)
        return rendered
