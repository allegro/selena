#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.db import connection, DatabaseError, transaction
from django.db.models import Max
from services.models import (Service, SlaDaily)
from django.utils import timezone

import logging

OFFSET_PERIOD = 7
WEEK = 7
ONE_MONTH = 1
THREE_MONTHS = 3
ONE_DAY_SECONDS = datetime.timedelta(days=1).total_seconds()

logger = logging.getLogger(__name__)

def calculatesla():
    max_service = _find_services_list()
    for service in max_service:
        last_day = _find_start_date(service['id'])
        diff = datetime.date.today() - last_day
        for day in range(diff.days):
            if day > 0:
                _calculate_SLA(day, service['id'])
        sla7d = '%.2f' % _calculate_cache(service['id'], timezone.now() - datetime.timedelta(days=WEEK))    # a week
        sla1m = '%.2f' % _calculate_cache(service['id'], _get_months_earlier(ONE_MONTH))                    # a month
        sla3m = '%.2f' % _calculate_cache(service['id'], _get_months_earlier(THREE_MONTHS))                 # three months
        _save_sla_to_cache(service['id'], sla7d, sla1m, sla3m)

# calculate SLA for particular day and selected service
def _calculate_SLA(offset, service):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=offset)
    # retrieve history. It take into account situation where one agent has a failure
    # and there is, at least, another one agent which reports success.
    sql = """
        SELECT created, response_state
        FROM services_servicehistory
        WHERE service_id = %s AND created >= %s AND created <= %s
        GROUP BY created
        ORDER BY created ASC, response_state ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, [ service,
                          start_time.strftime("%Y-%m-%d 00:00:01"),
                          start_time.strftime("%Y-%m-%d 23:59:59"),
    ])
    aggregated_failing_time_sec = 0
    break_found = False
    number_of_tries = 0
    for row in cursor.fetchall():
        number_of_tries += 1;
        if row[1] != 1:
            break_found = True
            diff_time = row[0] - start_time
            aggregated_failing_time_sec = aggregated_failing_time_sec + diff_time.total_seconds()
        else:
            # if previous check returned service down or performance issue, count the time to next proper
            # return as service break.
            if break_found == True:
                diff_time = row[0] - start_time
                aggregated_failing_time_sec = aggregated_failing_time_sec + diff_time.total_seconds()
            break_found = False
        start_time = row[0]
    # if there is at least one record in services_sevicehistory for selected service, calucate SLA
    # if the day has no records, lets assume, we are not able to calculate SLA
    if (number_of_tries > 0):
        # include last period: difference between last entry in servicehistory and 00:00:00 next day
        if break_found == True:
            stop_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=(offset-1))
            diff_time = stop_time - start_time
            aggregated_failing_time_sec += diff_time.total_seconds()
        data = {
            'service_id': service,
            'day': start_time,
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

#retrieve a list of active services
def _find_services_list():
    return Service.objects.filter(is_active=True).values('id')


def _find_start_date(service):
    last_day = SlaDaily.objects.annotate(max_date=Max('day')).filter(service_id__exact=service)
    if not last_day:
        return datetime.date.today() - datetime.timedelta(days=OFFSET_PERIOD)
    return last_day[0].max_date.date()

def _calculate_cache(service, yesterday):
    #get a day of last calculated SLA from DB
    service_sla = SlaDaily.objects.filter(service_id__exact=service, day__gte=yesterday.strftime("%Y-%m-%d 00:00:00%z")).values('day','sla')
    failing_time = 0
    counter = 0
    for row in service_sla:
        failing_time += ((100 - row['sla']) * ONE_DAY_SECONDS)/100
        counter += 1
    if (counter == 0):
        sla = -1
    else:
        sla = (100 - (failing_time/(ONE_DAY_SECONDS*counter)*100))
    return sla

def _get_months_earlier(offset):
    today = datetime.date.today()
    return_year = today.year
    if today.month - offset < 1:
        return_month = 12
        return_year = today.year - offset
    else:
        return_month = today.month - offset
    return timezone.now().replace(year = return_year, month = return_month, hour=0, minute=0, second=0, microsecond=0)

def _save_sla_to_cache(service, sla7d, sla1m, sla3m):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    data = {
        'service_id': service,
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

