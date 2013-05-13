#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import timedelta

from django.http import Http404
from django.utils import timezone

from boards.data_providers import get_probes_for_bar_chart
from .common import AjaxBase


class BarChart(AjaxBase):
    template_name = 'boards/bar_chart.html'

    def _get_probes(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        return get_probes_for_bar_chart(self.service_id, start_date, end_date)

    def get_context_data(self, **kwargs):
        ret = super(BarChart, self).get_context_data(**kwargs)
        ret.update({
            'probes': self._get_probes(),
        })
        return ret

    def get(self, *args, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        self.service_id = kwargs.get('service_id')
        return super(BarChart, self).get(*args, **kwargs)
