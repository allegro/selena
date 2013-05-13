#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.utils import timezone
import django_rq

from planner.models import TechnicalBreak


def _enable_and_disable_technical_breaks():
    now = timezone.now()
    planned_breaks = TechnicalBreak.objects.filter(
        activated=False,
        date_from__lte=now,
        date_to__gte=now,
    )
    for item in planned_breaks:
        service = item.service
        service.is_technical_break = True
        service.save()
        item.activated = True
        item.save()
    end_breaks = TechnicalBreak.objects.filter(
        activated=True,
        date_to__lte=now,
    )
    for item in end_breaks:
        service = item.service
        service.is_technical_break = False
        service.save()
        item.delete()


def enable_and_disable_technical_breaks():
    queue = django_rq.get_queue(
        name='planner' if 'planner' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_enable_and_disable_technical_breaks,
        timeout=180,
        result_ttl=0,
    )
