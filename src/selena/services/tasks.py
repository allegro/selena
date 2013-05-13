#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db import connection, DatabaseError, transaction
import django_rq

from services.monitoring import test_service
from services.models import Service


def _create_history_partitions():
    now = datetime.datetime.now()
    required_partitions = [
        (now + datetime.timedelta(days=1)).strftime("p%Y%m%d"),
        (now + datetime.timedelta(days=2)).strftime("p%Y%m%d"),
        (now + datetime.timedelta(days=3)).strftime("p%Y%m%d")
    ]
    partitions_conditions = {
        (now + datetime.timedelta(days=1)).strftime(
            "p%Y%m%d",
        ): (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        (now + datetime.timedelta(days=2)).strftime(
            "p%Y%m%d",
        ): (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
        (now + datetime.timedelta(days=3)).strftime(
            "p%Y%m%d",
        ): (now + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    }
    sql = """
        SELECT
            partition_name
        FROM INFORMATION_SCHEMA.PARTITIONS
        WHERE
            table_schema=%s AND
            table_name='services_servicehistory' AND
            partition_name<>'p_other'
        ORDER BY partition_name ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, [settings.DATABASES['default']['NAME']])
    current_partitions = []
    for row in cursor.fetchall():
        current_partitions.append(row[0])
    sql_parts = []
    for partition_name in required_partitions:
        if partition_name not in current_partitions:
            sql_parts.append(
                "PARTITION %s VALUES LESS THAN (TO_DAYS('%s'))" % (
                    partition_name, partitions_conditions[partition_name],
                ),
            )
    if not sql_parts:
        return
    sql = "ALTER TABLE services_servicehistory ADD PARTITION (%s)" % (
        ",".join(sql_parts),
    )
    cursor.execute(sql)


def create_history_partitions():
    queue = django_rq.get_queue(
        name='archiving' if 'archiving' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_create_history_partitions,
        timeout=300,
        result_ttl=0,
    )


def _create_archive_partitions():
    now = datetime.datetime.now()
    if now.month == 12:
        next_year = now.year + 1
        next_month = 1
    else:
        next_year = now.year
        next_month = now.month + 1
    next_month1 = datetime.date(next_year, next_month, 1)
    if next_month1.month == 12:
        next_year = next_month1.year + 1
        next_month = 1
    else:
        next_year = next_month1.year
        next_month = next_month1.month + 1
    next_month2 = datetime.date(next_year, next_month, 1)
    required_partitions = [
        next_month1.strftime("p%Y%m"),
        next_month2.strftime("p%Y%m")
    ]
    partitions_conditions = {
        next_month1.strftime("p%Y%m"): next_month1.strftime("%Y-%m-01"),
        next_month2.strftime("p%Y%m"): next_month2.strftime("%Y-%m-01"),
    }
    sql = """
        SELECT
            partition_name
        FROM INFORMATION_SCHEMA.PARTITIONS
        WHERE
            table_schema=%s AND
            table_name='services_servicehistoryarchive' AND
            partition_name<>'p_other'
        ORDER BY partition_name ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, [settings.DATABASES['default']['NAME']])
    current_partitions = []
    for row in cursor.fetchall():
        current_partitions.append(row[0])
    sql_parts = []
    for partition_name in required_partitions:
        if partition_name not in current_partitions:
            sql_parts.append(
                "PARTITION %s VALUES LESS THAN (TO_DAYS('%s'))" % (
                    partition_name, partitions_conditions[partition_name])
            )
    if not sql_parts:
        return
    sql = "ALTER TABLE services_servicehistoryarchive ADD PARTITION (%s)" % (
        ",".join(sql_parts),
    )
    cursor.execute(sql)


def create_archive_partitions():
    queue = django_rq.get_queue(
        name='archiving' if 'archiving' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_create_archive_partitions,
        timeout=300,
        result_ttl=0,
    )


def _make_history_archive():
    transaction.enter_transaction_management()
    transaction.managed()
    transaction.commit()
    date_start = datetime.datetime.now() - datetime.timedelta(days=8)
    sql = """
        SELECT MIN(id) AS min_id, MAX(id) AS max_id
        FROM services_servicehistory
        WHERE created >= %s AND created <= %s
        ORDER BY id DESC LIMIT 1
    """
    cursor = connection.cursor()
    cursor.execute(sql, [
        date_start.strftime("%Y-%m-%d 00:00:01"),
        date_start.strftime("%Y-%m-%d 23:59:59"),
    ])
    row = cursor.fetchone()
    if row is None:
        return
    min_deleted_id = row[0]
    max_deleted_id = row[1]
    if not min_deleted_id or not max_deleted_id:
        return
    sql = """
        INSERT INTO services_servicehistoryarchive (
            response_time,
            namelookup_time,
            connect_time,
            pretransfer_time,
            starttransfer_time,
            redirect_time,
            size_download,
            speed_download,
            redirect_count,
            num_connects,
            created,
            service_id,
            agent_id
        )
        SELECT
            ROUND(AVG(response_time), 2) AS response_time,
            ROUND(AVG(namelookup_time), 2) AS namelookup_time,
            ROUND(AVG(connect_time), 2) AS connect_time,
            ROUND(AVG(pretransfer_time), 2) AS pretransfer_time,
            ROUND(AVG(starttransfer_time), 2) AS starttransfer_time,
            ROUND(AVG(redirect_time), 2) AS redirect_time,
            ROUND(AVG(size_download), 0) AS size_download,
            ROUND(AVG(speed_download), 0) AS speed_download,
            ROUND(AVG(redirect_count), 0) AS redirect_count,
            ROUND(AVG(num_connects), 0) AS num_connects,
            CASE
                WHEN MINUTE(created) >= 45 THEN date_format(created, '%%Y-%%m-%%d %%H:45')
                WHEN MINUTE(created) < 45 AND MINUTE(created) >= 30 THEN date_format(created, '%%Y-%%m-%%d %%H:30')
                WHEN MINUTE(created) < 30 AND MINUTE(created) >= 15 THEN date_format(created, '%%Y-%%m-%%d %%H:15')
                ELSE date_format(created, '%%Y-%%m-%%d %%H:00')
            END AS created_at,
            service_id,
            agent_id
        FROM
            services_servicehistory
        WHERE
            created >= %s AND created <= %s
        GROUP BY
            created_at, service_id, agent_id;
    """
    try:
        cursor.execute(sql, [
            date_start.strftime("%Y-%m-%d 00:00:01"),
            date_start.strftime("%Y-%m-%d 23:59:59"),
        ])
    except DatabaseError:
        transaction.rollback()
        return
    sql = """
        DELETE FROM services_servicehistoryextra
        WHERE service_history_id >= %s AND service_history_id <= %s
    """
    try:
        cursor.execute(sql, [min_deleted_id, max_deleted_id])
    except DatabaseError:
        transaction.rollback()
        return
    sql = """
        SELECT
            partition_name
        FROM INFORMATION_SCHEMA.PARTITIONS
        WHERE
            table_schema=%s AND
            table_name='services_servicehistory' AND
            partition_name<>'p_other'
        ORDER BY partition_name ASC
    """
    try:
        cursor.execute(sql, [settings.DATABASES['default']['NAME']])
    except DatabaseError:
        transaction.rollback()
        return
    current_partitions = []
    for row in cursor.fetchall():
        current_partitions.append(row[0])
    partition_to_delete = (
        date_start + datetime.timedelta(days=1)
    ).strftime("p%Y%m%d")
    if partition_to_delete not in current_partitions:
        return
    sql = "ALTER TABLE services_servicehistory DROP PARTITION %s" % (
        partition_to_delete,
    )
    try:
        cursor.execute(sql)
    except DatabaseError:
        transaction.rollback()
        return
    transaction.commit()


def make_history_archive():
    queue = django_rq.get_queue(
        name='archiving' if 'archiving' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_make_history_archive,
        timeout=3600,
        result_ttl=0,
    )


def _monitor_service(service):
    test_service(service)


def monitor_all():
    queue = django_rq.get_queue(
        name='dispacher' if 'dispacher' in settings.RQ_QUEUES else 'default',
    )
    services = Service.objects.filter(is_technical_break=False, is_active=True)
    for service in services:
        queue.enqueue_call(
            func=_monitor_service,
            kwargs={'service': service},
            timeout=60,
            result_ttl=0,
        )
