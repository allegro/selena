#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from services.tasks import monitor_all


class Command(BaseCommand):
    help = 'Create required partitions'

    def handle(self, *args, **kwargs):
        monitor_all()
