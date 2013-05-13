#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import connection


CLASSIFICATION_ALL = 1
CLASSIFICATION_ONLY_CORE = 2
CLASSIFICATION_NOT_CORE = 3


def _get_index_data_sql(classification, errors_only, services):
    classification_sql = ''
    if classification == CLASSIFICATION_ONLY_CORE:
        classification_sql = 'AND S.is_core_service=1 '
    elif classification == CLASSIFICATION_NOT_CORE:
        classification_sql = 'AND S.is_core_service=0 '
    having_condition = """HAVING SUM(
        CASE WHEN SH.tick_failed=1 AND SH.main_probe=0 THEN 1 ELSE 0 END
    ) > 0""" if errors_only else ''
    services_condition = ''
    if services:
        services_condition = 'AND S.id IN (%s)' % ','.join(
            [str(service) for service in services],
        )
    sql = """
        SELECT
            S.id,
            S.name,
            S.url,
            S.is_core_service,
            SUM(
                CASE WHEN SH.response_state>1 THEN 1 ELSE 0 END
            ) AS have_problems,
            ROUND(MIN(SH.response_time), 2) AS min_response_time,
            ROUND(MAX(SH.response_time), 2) AS max_response_time,
            ROUND(AVG(SH.response_time), 2) AS avg_response_time
        FROM services_servicehistory AS SH
        JOIN services_service AS S ON S.id=SH.service_id
        WHERE SH.created>=%s AND SH.created<=%s AND S.is_active=1 {} {}
        GROUP BY S.name
        {}
        ORDER BY S.order ASC, S.name ASC
    """.format(classification_sql, services_condition, having_condition)
    return sql


def get_index_data(start_date, end_date, classification=CLASSIFICATION_ALL,
                   errors_only=False, services=[]):
    cursor = connection.cursor()
    cursor.execute(
        _get_index_data_sql(classification, errors_only, services),
        [
            start_date.strftime("%Y-%m-%d %H:%M"),
            end_date.strftime("%Y-%m-%d %H:%M"),
        ],
    )
    desc = cursor.description
    for row in cursor.fetchall():
        yield dict(zip([col[0] for col in desc], row))


def _get_probes_for_bar_chart_sql():
    return """
        SELECT
            service_id,
            CASE main_probe WHEN 0 THEN id ELSE main_probe END AS probe,
            SUM(
                CASE WHEN response_state > 1 THEN 1 ELSE 0 END
            ) AS problems_count,
            COUNT(id) AS probes_count,
            created
        FROM
            services_servicehistory
        WHERE
            service_id = %s AND created >= %s AND created <= %s
        GROUP BY probe
        ORDER BY created ASC
    """


def _get_probe_color(problems_count, probes_count):
    count = problems_count / 2
    if problems_count < (probes_count / 2):
        green = hex(255 - int(255 * count / probes_count))
        green = str(green)[2:]
        color = 'ff{0:>02}00'.format(green)
    else:
        red = hex(255 - int(255 * count / probes_count))
        red = str(red)[2:]
        color = '{0:>02}0000'.format(red)
    return color


def get_probes_for_bar_chart(service_id, start_date, end_date):
    cursor = connection.cursor()
    cursor.execute(
        _get_probes_for_bar_chart_sql(),
        [service_id, start_date, end_date],
    )
    desc = cursor.description
    for row in cursor.fetchall():
        data = dict(zip([col[0] for col in desc], row))
        if data['problems_count'] > 0:
            data.update({
                'color': _get_probe_color(
                    data['problems_count'],
                    data['probes_count'],
                ),
            })
        yield data


def get_history_items(start_date, stop_date, service_id=None):
    cursor = connection.cursor()
    params = [
        start_date.strftime("%Y-%m-%d 00:00:00"),
        stop_date.strftime("%Y-%m-%d 23:59:59"),
    ]
    sql = """
        SELECT
            SH.service_id,
            S.url,
            SH.response_state,
            SH.response_code,
            SH.response_time,
            SH.namelookup_time,
            SH.connect_time,
            SH.pretransfer_time,
            SH.starttransfer_time,
            SH.redirect_time,
            SH.size_download,
            SH.speed_download,
            SH.redirect_count,
            SH.num_connects,
            SH.agent_id,
            A.name,
            SH.created
        FROM services_servicehistory AS SH
        LEFT JOIN services_service AS S ON S.id = SH.service_id
        LEFT JOIN services_agent AS A ON A.id = SH.agent_id
        WHERE
            SH.response_state > 1 AND SH.created >= %s AND SH.created <= %s
    """
    if service_id:
        sql = sql + " AND S.id=%s"
        params.append(service_id)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        yield {
            'service_id': row[0],
            'url': row[1],
            'response_state': row[2],
            'response_code': row[3],
            'response_time': row[4],
            'namelookup_time': row[5],
            'connect_time': row[6],
            'pretransfer_time': row[7],
            'starttransfer_time': row[8],
            'redirect_time': row[9],
            'size_download': row[10],
            'speed_download': row[11],
            'redirect_count': row[12],
            'num_connects': row[13],
            'agent_id': row[14],
            'agent_name': row[15],
            'created': row[16]
        }
