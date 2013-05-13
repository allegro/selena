#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand

from services.tasks import (
    _make_history_archive,
    make_history_archive,
)


class Command(BaseCommand):
    help = 'Make archive'
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
            make_history_archive()
            return
        self.stdout.write('Make archive...')
        _make_history_archive()
        self.stdout.write('\nDone\n')
