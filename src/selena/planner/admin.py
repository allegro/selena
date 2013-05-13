#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

from planner.models import TechnicalBreak


class TechnicalBreakAdmin(admin.ModelAdmin):
    fields = ('short_desciption', 'service', 'date_from', 'date_to',)
    list_display = (
        'short_desciption', 'service', 'date_from', 'date_to', 'activated',
    )
    list_per_page = settings.DEFAULT_LIST_ITEMS_PER_PAGE
    list_filter = ('activated',)
    search_fields = ['short_desciption', ]

admin.site.register(TechnicalBreak, TechnicalBreakAdmin)
