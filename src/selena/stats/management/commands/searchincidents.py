#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand

from stats.tasks import _search_incidents, search_incidents


class Command(BaseCommand):
    help = 'Search noticed incidents'
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
            search_incidents()
            return
        self.stdout.write('Updating incidents data...')
        _search_incidents()
        self.stdout.write('\nDone\n')
