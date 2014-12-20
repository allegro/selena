#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from django.db.models.aggregates import Min

from services.models import (Service, SlaDaily, SlaCache, ServiceHistory)
from django.utils import timezone
from dateutil.relativedelta import *
from django.core.exceptions import ObjectDoesNotExist
import datetime
import logging

OFFSET_PERIOD = 7
WEEK = 7
ONE_MONTH = 1
THREE_MONTHS = 3
ONE_DAY_SECONDS = datetime.timedelta(days=1).total_seconds()

logger = logging.getLogger(__name__)


def calculatesla():
    # SlaCache object for bulk create
    sla_cache_create = []

    services = Service.objects.filter(is_active=True).only('id').order_by('id')
    for service in services:
        last_day = _find_start_date(service)
        diff = datetime.date.today() - last_day
        for day in range(diff.days):
            if day > 0:
                _calculate_SLA(day, service)

        sla7d = '%.2f' % _calculate_cache(service, timezone.now() - datetime.timedelta(days=WEEK))
        sla1m = '%.2f' % _calculate_cache(service, timezone.now() + relativedelta(months=-ONE_MONTH))
        sla3m = '%.2f' % _calculate_cache(service, timezone.now() + relativedelta(months=-THREE_MONTHS))
        # create SlaCache and append it to list
        sla_cache_create.append(SlaCache(service_id=service.id,
                                         sla7days=sla7d,
                                         sla1month=sla1m,
                                         sla3months=sla3m))

    # delete all cache objects.
    SlaCache.objects.filter(pk__in=[sc.service_id for sc in sla_cache_create]).delete()
    # create all SlaCache objects in bulk.
    SlaCache.objects.bulk_create(sla_cache_create)


# calculate SLA for particular day and selected service
def _calculate_SLA(offset, service):
    UTC_NOW = timezone.now()
    LOCAL_NOW = timezone.localtime(UTC_NOW)
    TIME_OFFSET = LOCAL_NOW.utcoffset()

    utc_start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=offset)
    utc_stop_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=(offset-1))
    local_start_time = utc_start_time - TIME_OFFSET
    local_stop_time = utc_stop_time - TIME_OFFSET

    # retrieve history. It take into account situation where one agent has a failure
    # and there is, at least, another one agent which reports success.

    service_history = ServiceHistory.objects.values('created').\
        filter(service_id=service.id).\
        filter(created__gt=local_start_time).\
        filter(created__lt=local_stop_time).\
        filter(response_state__lt=5).\
        annotate(response_state=Min('response_state')).\
        order_by('created', 'response_state')

    aggregated_failing_time_sec = 0
    break_found = False
    number_of_tries = 0
    _start_time = local_start_time

    for s_history in service_history:
        number_of_tries += 1
        if s_history['response_state'] != 1:
            break_found = True
            diff_time = s_history['created'] - _start_time
            aggregated_failing_time_sec += diff_time.total_seconds()
        else:
            # if previous check returned service down or performance issue, count the time to next proper
            # return as service break.
            if break_found:
                diff_time = s_history['created'] - _start_time
                aggregated_failing_time_sec += diff_time.total_seconds()
            break_found = False
        _start_time = s_history['created']

    # if there is at least one record in services_sevicehistory for selected service, calucate SLA
    # if the day has no records, lets assume, we are not able to calculate SLA
    if number_of_tries > 0:
        # include last period: difference between last entry in servicehistory and 00:00:00 UTC next day
        if break_found:
            diff_time = local_stop_time - _start_time
            aggregated_failing_time_sec += diff_time.total_seconds()

        sla_value = (100 - (aggregated_failing_time_sec/ONE_DAY_SECONDS*100))
        sla_daily = SlaDaily(service_id=service.id, day=utc_start_time, sla=sla_value)
        sla_daily.save()


def _find_start_date(service):
    try:
        last_day = SlaDaily.objects.filter(service_id__exact=service.id).latest('day')
    except ObjectDoesNotExist:
        return datetime.date.today() - datetime.timedelta(days=OFFSET_PERIOD)
    return last_day.day.date()


def _calculate_cache(service, yesterday):
    delta_days = timezone.now() - yesterday
    service_sla = SlaDaily.objects.filter(service_id__exact=service.id,
                                          day__gte=yesterday.strftime("%Y-%m-%d 00:00:00%z")).values('day', 'sla')
    failing_time = 0
    counter = 0
    for row in service_sla:
        failing_time += ((100 - row['sla']) * ONE_DAY_SECONDS) / 100
        counter += 1
    if counter == 0:
        sla = -1
    else:
        sla = (100 - (failing_time / (ONE_DAY_SECONDS * delta_days.days) * 100))
    return sla

