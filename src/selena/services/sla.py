#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from pytz import timezone

from django.db import connection, DatabaseError, transaction

OFFSET_PERIOD = 7
WEEK = 7
THREE_MONTHS = 3
ONE_DAY_SECONDS = datetime.timedelta(days=1).total_seconds()

def calculatesla():
    max_service = _find_services_list()
    for service in max_service:
        last_day = _find_start_date(service[0])
        diff = datetime.date.today() - last_day
        for day in range(diff.days):
            if day > 0:
                _calculate_SLA(day, service[0])
        sla7d = '%.2f' % _calculate_cache(service[0], datetime.date.today() - datetime.timedelta(days=WEEK))    # a week
        sla1m = '%.2f' % _calculate_cache(service[0], _get_month_earlier(datetime.date.today()))                # a month
        sla3m = '%.2f' % _calculate_cache(service[0], _get_months_earlier(datetime.date.today(), THREE_MONTHS)) # three months
        _save_sla_to_cache(service[0], sla7d, sla1m, sla3m)

# calculate SLA for particular day and selected service
def _calculate_SLA(offset, service):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    yesterday = datetime.date.today() - datetime.timedelta(days=offset)
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
        yesterday.strftime("%Y-%m-%d 00:00:01"),
        yesterday.strftime("%Y-%m-%d 23:59:59"),
    ])
    here = timezone('UTC')
    start_time_naive = datetime.datetime.combine(yesterday, datetime.time())
    start_time = here.localize(start_time_naive)
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
            today = datetime.date.today() - datetime.timedelta(days=(offset-1))
            stop_time_naive = datetime.datetime.combine(today, datetime.time())
            stop_time = here.localize(stop_time_naive)
            diff_time = stop_time - start_time
            aggregated_failing_time_sec += diff_time.total_seconds()
        data = {
            'service_id': service,
            'day': yesterday,
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
            # print("DB error %s", e)
            return
    cursor.close()

#retrieve a list of active services
def _find_services_list():
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    sql = """
        SELECT id
        FROM services_service
        WHERE is_active = %s
    """
    cursor = connection.cursor()
    cursor.execute(sql, [ 1 ])
    row = cursor.fetchall()
    return row


def _find_start_date(service):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    #get a day of last calculated SLA from DB
    sql = """
        SELECT max(day)
        FROM services_sladaily
        WHERE service_id = %s
    """
    cursor = connection.cursor()
    cursor.execute(sql, [ service ])
    row = cursor.fetchone()
    if row[0] is None:
        cursor.close()
        # if the day is not known, get OFFSET_PERIOD as a maximum history to calculate SLA
        return datetime.date.today() - datetime.timedelta(days=OFFSET_PERIOD)
    return_date = row[0].date()
    cursor.close()
    return return_date

def _calculate_cache(service, yesterday):
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    #get a day of last calculated SLA from DB
    sql = """
        SELECT day, sla
        FROM services_sladaily
        WHERE service_id = %s AND day >= %s
    """
    cursor = connection.cursor()
    cursor.execute(sql, [ service, yesterday.strftime("%Y-%m-%d 00:00:01") ])
    failing_time = 0
    counter = 0
    for row in cursor.fetchall():
        failing_time += ((100 - row[1]) * ONE_DAY_SECONDS)/100
        counter += 1
    if (counter == 0):
        sla = -1
    else:
        sla = (100 - (failing_time/(ONE_DAY_SECONDS*counter)*100))
    return sla

def _get_month_earlier(time):
    #Note that the resultant day of the month might change if the following
    #month has fewer days:
    #
    #    >>> _get_month_earlier(datetime.date(2010, 3, 31))
    #    datetime.date(2010, 2, 28)
    one_day = datetime.timedelta(days=1)
    one_month_earlier = time - one_day
    while one_month_earlier.month == time.month or one_month_earlier.day > time.day:
        one_month_earlier -= one_day
    return one_month_earlier

def _get_months_earlier(time, number_of_months):
    _time = time
    for x in range(number_of_months):
        _time = _get_month_earlier(_time)
    return _time

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
        # print("DB error %s", e)
        return
    cursor.close()