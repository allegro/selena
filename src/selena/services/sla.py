#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import connection, DatabaseError, transaction
from services.models import (Service, SlaDaily)
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
    services = Service.objects.filter(is_active=True)
    for service in services:
        last_day = _find_start_date(service)
        diff = datetime.date.today() - last_day
        for day in range(diff.days):
            if day > 0:
                _calculate_SLA(day, service)
        sla7d = '%.2f' % _calculate_cache(service, timezone.now() - datetime.timedelta(days=WEEK))
        sla1m = '%.2f' % _calculate_cache(service, timezone.now() + relativedelta(months=-ONE_MONTH))
        sla3m = '%.2f' % _calculate_cache(service, timezone.now() + relativedelta(months=-THREE_MONTHS))
        _save_sla_to_cache(service, sla7d, sla1m, sla3m)

# calculate SLA for particular day and selected service
def _calculate_SLA(offset, service):
    UTC_NOW = timezone.now()
    LOCAL_NOW = timezone.localtime(UTC_NOW)
    TIME_OFFSET = LOCAL_NOW.utcoffset()

    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()

    utc_start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=offset)
    utc_stop_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=(offset-1))
    local_start_time = utc_start_time - TIME_OFFSET
    local_stop_time = utc_stop_time - TIME_OFFSET

    # retrieve history. It take into account situation where one agent has a failure
    # and there is, at least, another one agent which reports success.
    sql = """
        SELECT created, response_state
        FROM services_servicehistory
        WHERE service_id = %s AND created > %s AND created < %s AND response_state < 5
        GROUP BY created
        ORDER BY created ASC, response_state ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, [ service.id,
                          local_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                          local_stop_time.strftime("%Y-%m-%d %H:%M:%S"),
    ])
    aggregated_failing_time_sec = 0
    break_found = False
    number_of_tries = 0
    _start_time = local_start_time
    for row in cursor.fetchall():
        number_of_tries += 1;
        if row[1] != 1:
            break_found = True
            diff_time = row[0] - _start_time
            aggregated_failing_time_sec = aggregated_failing_time_sec + diff_time.total_seconds()
        else:
            # if previous check returned service down or performance issue, count the time to next proper
            # return as service break.
            if break_found == True:
                diff_time = row[0] - _start_time
                aggregated_failing_time_sec = aggregated_failing_time_sec + diff_time.total_seconds()
            break_found = False
        _start_time = row[0]
    # if there is at least one record in services_sevicehistory for selected service, calucate SLA
    # if the day has no records, lets assume, we are not able to calculate SLA
    if (number_of_tries > 0):
        # include last period: difference between last entry in servicehistory and 00:00:00 UTC next day
        if break_found:
            diff_time = local_stop_time - _start_time
            aggregated_failing_time_sec += diff_time.total_seconds()
        data = {
            'service_id': service.id,
            'day': utc_start_time,
            'sla': (100 - (aggregated_failing_time_sec/ONE_DAY_SECONDS*100)),
            }
        sql = """
            INSERT INTO services_sladaily (service_id, day, sla) VALUES (%(service_id)s, %(day)s, %(sla)s )
        """
        try:
            cursor.execute(sql, data)
            transaction.commit()
        except DatabaseError as e:
            transaction.rollback()
            _message = 'DB error %s' % e
            logger.error(_message)
            return
    cursor.close()

def _find_start_date(service):
    try:
        last_day = SlaDaily.objects.filter(service_id__exact=service.id).latest('day')
    except ObjectDoesNotExist:
        return datetime.date.today() - datetime.timedelta(days=OFFSET_PERIOD)
    return last_day.day.date()

def _calculate_cache(service, yesterday):
    delta_days = timezone.now() - yesterday
    service_sla = SlaDaily.objects.filter(service_id__exact=service.id, day__gte=yesterday.strftime("%Y-%m-%d 00:00:00%z")).values('day','sla')
    failing_time = 0
    counter = 0
    for row in service_sla:
        failing_time += ((100 - row['sla']) * ONE_DAY_SECONDS)/100
        counter += 1
    if (counter == 0):
        sla = -1
    else:
        sla = (100 - (failing_time/(ONE_DAY_SECONDS*delta_days.days)*100))
    return sla

def _save_sla_to_cache(service, sla7d, sla1m, sla3m):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    data = {
        'service_id': service.id,
        'sla7days': sla7d,
        'sla1month': sla1m,
        'sla3months': sla3m,
        }
    sql = """
            INSERT INTO services_slacache (service_id, sla7days, sla1month, sla3months)
            VALUES (%(service_id)s, %(sla7days)s, %(sla1month)s, %(sla3months)s )
            ON DUPLICATE KEY UPDATE sla7days=%(sla7days)s, sla1month=%(sla1month)s, sla3months=%(sla3months)s
        """
    try:
        cursor = connection.cursor()
        cursor.execute(sql, data)
        transaction.commit()
    except DatabaseError as e:
        transaction.rollback()
        _message = 'DB error %s' % e
        logger.error(_message)
        return
    cursor.close()

