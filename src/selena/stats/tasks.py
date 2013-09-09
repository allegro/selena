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
    # checking if any incidents can be closed
    ok_services_ids = []
    for open_incident in Incident.objects.filter(is_closed=False):
        working_min_probes_count = Service.objects.get(
            pk=open_incident.service_id
        ).service_working_min_probes_count
        start_date = now - datetime.timedelta(minutes=working_min_probes_count)
        ret = get_real_problems_number(
            ServiceHistory.objects.filter(
                service_id=open_incident.service_id,
                created__gt=start_date,
                created__lte=now,
            ).order_by('created'),
            ok_mode=True,
        )
        if ret['real_problems_number'] == working_min_probes_count:
            open_incident.is_closed = True
            open_incident.end_date = start_date
        else:
            open_incident.end_date = now
        open_incident.save()
    active_services_ids = Service.objects.filter(
        is_active=True,
        is_technical_break=False,
    ).values_list('id', flat=True)
    start_date = now - datetime.timedelta(minutes=2)
    services_with_problems = ServiceHistory.objects.filter(
        service_id__in=active_services_ids,
        response_state__in=(2, 3),
        created__gt=start_date,
        created__lt=now,
    ).values(
        'service_id',
    ).order_by('-created')

    for item in services_with_problems:
        service = None
        try:
            service = Service.objects.get(
                pk=item['service_id'],
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
            ok_mode=False,
            get_first_and_last_broken_probes=True,
        )
        if ret['real_problems_number'] == service.time_delta:
            try:
                incident = Incident.objects.get(
                    service=service,
                    is_closed=False,
                )
            except Incident.DoesNotExist:
                incident = Incident(
                    service=service,
                    start_date=ret['first_broken_probe'].created,
                    end_date=ret['last_broken_probe'].created,
                    is_closed=False,
                )
            incident.incident_type = ret['problem_type']
            incident.save()


def search_incidents():
    queue = django_rq.get_queue(
        name='stats' if 'stats' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_search_incidents,
        timeout=180,
        result_ttl=0,
    )
