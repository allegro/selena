#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cStringIO

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404

from boards.csv_utils import UnicodeWriter
from boards.data_providers import get_history_items
from boards.forms import CSVErrorsReportForm, DateAndTimeRangeForm
from services.models import (
    Agent,
    ResponseStateChoices,
    Service,
    ServiceHistory,
)
from .common import Base


class FullHistory(Base):
    template_name = 'boards/full_history.html'

    def get_context_data(self, **kwargs):
        ret = super(FullHistory, self).get_context_data(**kwargs)
        url_params = self.request.GET.copy()
        try:
            del url_params['page']
        except KeyError:
            pass
        url_params = url_params.urlencode()
        ret.update({
            'form': self.form,
            'service': self.service,
            'history': self.history,
            'params': self.service.additionalrequestparam_set.all(),
            'agents': Agent.objects.all(),
            'url_params': url_params,
        })
        return ret

    def get(self, *args, **kwargs):
        self.service = get_object_or_404(
            Service,
            id=kwargs.get('service_id'),
            is_active=True,
        )
        if self.request.GET and len(self.request.GET) >= 4:
            self.form = DateAndTimeRangeForm(self.request.GET)
        else:
            self.form = DateAndTimeRangeForm(
                data={
                    'start_date': timezone.now().strftime("%Y-%m-%d"),
                    'stop_date': timezone.now().strftime("%Y-%m-%d"),
                    'start_time': '00:00',
                    'stop_time': '23:59',
                },
            )
        self.history = None
        if self.form.is_valid():
            start_date = self.form.cleaned_data['start_date']
            start_time = self.form.cleaned_data['start_time']
            from_date = timezone.datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
                hour=start_time.hour,
                minute=start_time.minute,
            )
            stop_date = self.form.cleaned_data['stop_date']
            stop_time = self.form.cleaned_data['stop_time']
            to_date = timezone.datetime(
                year=stop_date.year,
                month=stop_date.month,
                day=stop_date.day,
                hour=stop_time.hour,
                minute=stop_time.minute,
            )
            paginator = Paginator(
                ServiceHistory.objects.filter(
                    service_id=self.service.id,
                    created__gte=from_date,
                    created__lte=to_date,
                ), 60,
            )
            page = self.request.GET.get('page', 1)
            try:
                self.history = paginator.page(page)
            except PageNotAnInteger:
                self.history = paginator.page(1)
            except EmptyPage:
                self.history = paginator.page(paginator.num_pages)
        return super(FullHistory, self).get(*args, **kwargs)


class CSVErrorsReport(Base):
    template_name = 'boards/csv_report.html'

    def _get_data(self, start_date, stop_date, service_id=None):
        yield [
            'service_id', 'url', 'response_state_id', 'response_state',
            'response_code', 'response_time', 'namelookup_time',
            'connect_time', 'pretransfer_time', 'starttransfer_time',
            'redirect_time', 'size_download', 'speed_download',
            'redirect_count', 'num_connects', 'agent_id', 'agent_name',
            'created',
        ]
        response_states = ResponseStateChoices()
        for item in get_history_items(start_date, stop_date, service_id):
            yield [
                item['service_id'],
                item['url'],
                item['response_state'],
                response_states.from_id(item['response_state']).name,
                item['response_code'],
                item['response_time'],
                item['namelookup_time'],
                item['connect_time'],
                item['pretransfer_time'],
                item['starttransfer_time'],
                item['redirect_time'],
                item['size_download'],
                item['speed_download'],
                item['redirect_count'],
                item['num_connects'],
                item['agent_id'],
                item['agent_name'],
                timezone.localtime(
                    item['created'],
                ).strftime("%Y-%m-%d %H:%M:%S"),
            ]

    def get_context_data(self, **kwargs):
        ret = super(CSVErrorsReport, self).get_context_data(**kwargs)
        ret.update({
            'form': self.form,
        })
        return ret

    def get(self, *args, **kwargs):
        self.form = CSVErrorsReportForm(
            initial={
                'start_date': timezone.now().strftime("%Y-%m-%d"),
                'stop_date': timezone.now().strftime("%Y-%m-%d"),
            },
        )
        return super(CSVErrorsReport, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.form = CSVErrorsReportForm(self.request.POST)
        if self.form.is_valid():
            start_date = self.form.cleaned_data['start_date']
            stop_date = self.form.cleaned_data['stop_date']
            service_id = self.form.cleaned_data.get('service', None)
            f = cStringIO.StringIO()
            UnicodeWriter(f).writerows(
                (unicode(item) for item in row) for row in self._get_data(
                    start_date=start_date,
                    stop_date=stop_date,
                    service_id=service_id,
                ),
            )
            response = HttpResponse(
                f.getvalue(),
                content_type='application/csv',
            )
            filename = 'report_%s_%s.csv' % (
                start_date.strftime("%Y-%m-%d"),
                stop_date.strftime("%Y-%m-%d"),
            )
            disposition = 'attachment; filename=%s' % filename
            response['Content-Disposition'] = disposition
            return response
        return super(CSVErrorsReport, self).get(*args, **kwargs)
