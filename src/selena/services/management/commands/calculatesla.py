#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from services.sla import calculatesla


class Command(BaseCommand):
    help = 'Calculate SLA for desired services'

    def handle(self, *args, **kwargs):
        calculatesla()
