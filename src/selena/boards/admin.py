#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings

from boards.models import Board


class BoardAmin(admin.ModelAdmin):
    fields = ('name', 'services',)
    list_display = ('name',)
    list_per_page = settings.DEFAULT_LIST_ITEMS_PER_PAGE
    search_fields = ['name', ]
    filter_horizontal = ('services',)

admin.site.register(Board, BoardAmin)
