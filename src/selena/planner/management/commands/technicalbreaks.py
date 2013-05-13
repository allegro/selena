#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand

from planner.tasks import (
    _enable_and_disable_technical_breaks,
    enable_and_disable_technical_breaks,
)


class Command(BaseCommand):
    help = 'Enable or disable planned technical breaks'
    option_list = BaseCommand.option_list + (
        make_option(
            '--async-mode',
            dest='async_mode',
            default=False,
            help='If True this task will be enqueued.',
            type='int',
        ),
    )

    def handle(self, *args, **kwargs):
        async_mode = kwargs.get('async_mode', 0)
        if async_mode == 1:
            enable_and_disable_technical_breaks()
            return
        self.stdout.write('Enable or disable breaks...')
        _enable_and_disable_technical_breaks()
        self.stdout.write('\nDone\n')
