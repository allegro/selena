#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand

from services.tasks import (
    _create_archive_partitions,
    _create_history_partitions,
    create_archive_partitions,
    create_history_partitions,
)


class Command(BaseCommand):
    help = 'Create required partitions'
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
            create_history_partitions()
            create_archive_partitions()
            return
        self.stdout.write('Create history partitions...')
        _create_history_partitions()
        self.stdout.write('\tDone\n')
        self.stdout.write('Create archive partitions...')
        _create_archive_partitions()
        self.stdout.write('\tDone\n')
