#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db.models import Count
from django.utils import timezone
import django_rq

from services.models import Service, ServiceHistory
from stats.models import Incident
from stats.utils import get_real_problems_number


def _search_incidents():
    now = timezone.now()
    start_date = now - datetime.timedelta(minutes=5)
    technical_breaks = Service.objects.filter(
        is_active=True,
        is_technical_break=True,
    )
    technical_breaks_ids = [item.pk for item in technical_breaks]
    parsed_services = []
    not_working_services = ServiceHistory.objects.exclude(
        service_id__in=technical_breaks_ids,
    ).filter(
        response_state=3,
        created__gt=start_date,
        created__lt=now,
    ).values(
        'service_id',
    ).annotate(
        problems_number=Count('response_state'),
    ).order_by('-created')
    for item in not_working_services:
        service = None
        try:
            service = Service.objects.get(
                pk=item['service_id'],
                is_active=True,
            )
        except Service.DoesNotExist:
            continue
        to_date = timezone.now()
        since_date = to_date - datetime.timedelta(
            minutes=service.time_delta,
        )
        ret = get_real_problems_number(
            ServiceHistory.objects.filter(
                service_id=service.pk,
                created__gt=since_date,
                created__lt=to_date
            ).order_by('-created'),
            die_services_mode=True,
            get_first_and_last_broken_probes=True,
        )
        if ret['real_problems_number'] >= service.service_not_working_min_probes_count:
            try:
                incident = Incident.objects.get(
                    service=service,
                    is_closed=False,
                )
                incident.end_date = ret['last_broken_probe'].created
            except Incident.DoesNotExist:
                incident = Incident(
                    service=service,
                    start_date=ret['first_broken_probe'].created,
                    end_date=ret['last_broken_probe'].created,
                    is_closed=False,
                )
            incident.save()
            parsed_services.append(service.pk)
    services_with_problems = ServiceHistory.objects.exclude(
        service_id__in=technical_breaks_ids,
    ).filter(
        response_state=2,
        created__gt=start_date,
        created__lt=now,
    ).values(
        'service_id',
    ).annotate(
        problems_number=Count('response_state'),
    ).order_by('-created')
    for item in services_with_problems:
        if int(item['service_id']) in parsed_services:
            continue
        service = None
        try:
            service = Service.objects.get(
                pk=item['service_id'],
                is_active=True,
            )
        except Service.DoesNotExist:
            continue
        to_date = timezone.now()
        since_date = to_date - datetime.timedelta(minutes=service.time_delta)
        ret = get_real_problems_number(
            ServiceHistory.objects.filter(
                service_id=service.pk,
                created__gt=since_date,
                created__lt=to_date,
            ).order_by('-created'),
            die_services_mode=False,
            get_first_and_last_broken_probes=True,
        )
        if ret['real_problems_number'] >= service.performance_issues_min_probes_count:
            try:
                incident = Incident.objects.get(
                    service=service,
                    is_closed=False,
                )
                incident.end_date = ret['last_broken_probe'].created
            except Incident.DoesNotExist:
                incident = Incident(
                    service=service,
                    start_date=ret['first_broken_probe'].created,
                    end_date=ret['last_broken_probe'].created,
                    is_closed=False,
                )
            incident.save()
            parsed_services.append(service.pk)
    open_incidents = Incident.objects.filter(is_closed=False)
    for open_incident in open_incidents:
        if open_incident.service.pk not in parsed_services:
            open_incident.is_closed = True
            open_incident.save()


def search_incidents():
    queue = django_rq.get_queue(
        name='stats' if 'stats' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_search_incidents,
        timeout=180,
        result_ttl=0,
    )
