#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import timedelta, datetime

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404

from boards.data_providers import (
    CLASSIFICATION_NOT_CORE,
    CLASSIFICATION_ONLY_CORE,
    get_index_data,
)
from boards.models import Board
from services.models import (
    AdditionalRequestParam,
    Agent,
    ResponseStateChoices,
    Service,
    ServiceHistory,
    ServiceHistoryExtra,
)
from .common import AjaxBase, Base


class Home(Base):
    template_name = 'boards/index.html'

    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        return get_index_data(start_date, end_date)

    def get_context_data(self, **kwargs):
        ret = super(Home, self).get_context_data(**kwargs)
        ret.update({
            'items': self._get_items()
        })
        return ret


class CoreServices(Home):
    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        return get_index_data(
            start_date,
            end_date,
            classification=CLASSIFICATION_ONLY_CORE,
        )


class ErrorsOnly(Home):
    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(minutes=settings.ERROR_TIME_INTERVAL)
        return get_index_data(
            start_date,
            end_date,
            errors_only=True,
        )


class CoreServicesErrorsOnly(Home):
    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(minutes=settings.ERROR_TIME_INTERVAL)
        return get_index_data(
            start_date,
            end_date,
            classification=CLASSIFICATION_ONLY_CORE,
            errors_only=True,
        )


class NotCoreServices(Home):
    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        return get_index_data(
            start_date,
            end_date,
            classification=CLASSIFICATION_NOT_CORE,
        )


class CustomBoards(Home):
    def _get_items(self):
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        services = self.board.services.filter(
            is_active=True,
        ).values_list('id', flat=True)
        return get_index_data(
            start_date,
            end_date,
            services=services,
        )

    def get(self, *args, **kwargs):
        self.board = get_object_or_404(Board, id=kwargs.get('board_id'))
        return super(CustomBoards, self).get(*args, **kwargs)


class ServiceDetails(Base):
    template_name = 'boards/service_details.html'

    def _get_charts_data(self):
        agents_names = {}
        for agent in Agent.objects.all():
            agents_names[agent.pk] = agent.name
        params_names = {}
        for param in self.service.additionalrequestparam_set.all():
            params_names[param.id] = param.name
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=1)
        raw_probes = ServiceHistory.objects.filter(
            service_id=self.service.id,
            created__gte=start_date,
            created__lte=end_date,
        ).values(
            'id',
            'response_state',
            'request_params_id',
            'agent_id',
            'main_probe',
            'created',
            'response_time',
            'namelookup_time',
            'connect_time',
            'pretransfer_time',
            'starttransfer_time',
        ).order_by('created', 'main_probe')
        grouped_probes = {}
        for probe in raw_probes:
            if not probe['main_probe']:
                grouped_probes[probe['id']] = [probe]
            else:
                grouped_probes[probe['main_probe']].append(probe)
        groups = {}
        for probe_id, probes in grouped_probes.items():
            for probe in probes:
                group_id = 'g_%s_%s' % (
                    probe['agent_id'],
                    probe['request_params_id']
                    if probe['request_params_id'] else '',
                )
                group_name = '%s%s' % (
                    agents_names.get(probe['agent_id'], ''),
                    ' (%s)' % params_names.get(probe['request_params_id'], '')
                    if probe['request_params_id'] else '',
                )
                group = groups.get(
                    group_id,
                    {
                        'group_id': group_id,
                        'group_items': [],
                        'group_name': group_name,
                    }
                )
                group['group_items'].append(probe)
                groups[group_id] = group
        data = []
        for group_id, group in groups.items():
            data.append({
                'group_id': group_id,
                'group_name': group['group_name'],
                'group_items': sorted(
                    group['group_items'],
                    key=lambda k: k['created'],
                )
            })
        return data

    def get_context_data(self, **kwargs):
        ret = super(ServiceDetails, self).get_context_data(**kwargs)
        paginator = Paginator(
            ServiceHistory.objects.filter(service_id=self.service.id), 60,
        )
        page = self.request.GET.get('page', 1)
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            history = paginator.page(1)
        except EmptyPage:
            history = paginator.page(paginator.num_pages)
        ret.update({
            'service': self.service,
            'phrases': self.service.monitoredphrase_set.filter(
                is_active=True,
            ),
            'params': self.service.additionalrequestparam_set.all(),
            'history': history,
            'agents': Agent.objects.all(),
            'probes': self._get_charts_data(),
        })
        return ret

    def get(self, *args, **kwargs):
        self.service = get_object_or_404(
            Service,
            id=kwargs.get('service_id'),
            is_active=True,
        )
        return super(ServiceDetails, self).get(*args, **kwargs)


class ErrorMessage(AjaxBase):
    template_name = 'boards/error_msg.html'

    def get_context_data(self, **kwargs):
        ret = super(ErrorMessage, self).get_context_data(**kwargs)
        try:
            info = ServiceHistoryExtra.objects.filter(
                service_history_id=self.probe_id,
            )[0]
        except IndexError:
            message = ''
        else:
            message = "Error: %s;" % info.error_msg if info.error_msg else ""
            if info.wordchecks_errors:
                if info.error_msg:
                    message = "%s Words checks errors: %s;" % (
                        message,
                        info.wordchecks_errors,
                    )
                else:
                    message = "Words checks errors: %s;" % (
                        info.wordchecks_errors,
                    )
        ret.update({
            'message': message,
        })
        return ret

    def get(self, *args, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        self.probe_id = kwargs.get('probe_id')
        return super(ErrorMessage, self).get(*args, **kwargs)


class ProbeDetails(AjaxBase):
    template_name = 'boards/probe_details.html'

    def _get_data(self):
        today = timezone.now().date()
        cases = []
        total_num = 0
        fail_num = 0
        for probe in ServiceHistory.objects.filter(
            Q(id=self.probe_id) | Q(main_probe=self.probe_id),
            created__year=today.year,
            created__month=today.month,
            created__day=today.day,
        ):
            try:
                agent = Agent.objects.get(id=probe.agent_id).name
            except Agent.DoesNotExist:
                continue
            param = ''
            if probe.request_params_id:
                try:
                    param = AdditionalRequestParam.objects.get(
                        id=probe.request_params_id,
                    ).name
                except AdditionalRequestParam.DoesNotExist:
                    continue
            cases.append({
                'agent_name': agent,
                'request_params_name': param,
                'state': ResponseStateChoices.raw_from_id(
                    probe.response_state,
                ),
            })
            if probe.response_state != ResponseStateChoices.ok:
                fail_num += 1
            total_num += 1
        return cases, fail_num, total_num

    def get_context_data(self, **kwargs):
        ret = super(ProbeDetails, self).get_context_data(**kwargs)
        cases, fail_num, total_num = self._get_data()
        ret.update({
            'cases': cases,
            'fail_num': fail_num,
            'total_num': total_num,
        })
        return ret

    def get(self, *args, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        self.probe_id = kwargs.get('probe_id')
        return super(ProbeDetails, self).get(*args, **kwargs)
