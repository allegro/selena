#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _

from boards.models import Board


class BaseMixin(object):
    def get_context_data(self, **kwargs):
        ret = super(BaseMixin, self).get_context_data(**kwargs)
        ret.update({
            'mainmenu_items': [
                {'name': _('All'), 'href': '/'},
                {'name': _('Errors only'), 'href': '/mode/errors-only'},
                {'name': _('Core services'), 'href': '/mode/core-services'},
                {
                    'name': _('Core services errors only'),
                    'href': '/mode/core-services-errors-only',
                },
                {
                    'name': _('Non-core services'),
                    'href': '/mode/non-core-services',
                },
            ],
            'additionalmenu_items': [
                {
                    'name': _('Generate errors report'),
                    'href': '/generate-errors-report',
                },
                {'name': _('Admin panel'), 'href': '/admin'},
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
