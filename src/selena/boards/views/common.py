#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView

from boards.models import Board


class BaseMixin(object):
    def get_context_data(self, **kwargs):
        ret = super(BaseMixin, self).get_context_data(**kwargs)
        ret.update({
            'mainmenu_items': [
                {'name': 'All', 'href': '/'},
                {'name': 'Errors only', 'href': '/mode/errors-only'},
                {'name': 'Core services', 'href': '/mode/core-services'},
                {
                    'name': 'Core services errors only',
                    'href': '/mode/core-services-errors-only',
                },
                {
                    'name': 'Non-core services',
                    'href': '/mode/non-core-services',
                },
            ],
            'additionalmenu_items': [
                {
                    'name': 'Generate errors report',
                    'href': '/generate-errors-report',
                },
                {'name': 'Admin panel', 'href': '/admin'},
            ],
        })
        return ret


class Base(BaseMixin, TemplateView):
    def get_context_data(self, **kwargs):
        ret = super(Base, self).get_context_data(**kwargs)
        ret.update({
            'boards': Board.objects.all(),
        })
        return ret


class AjaxBase(TemplateView):
    pass
