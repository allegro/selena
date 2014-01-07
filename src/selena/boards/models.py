#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from services.models import Service


class Board(models.Model):
    name = models.CharField(_('name'), max_length=250)
    services = models.ManyToManyField(Service, verbose_name=_('services'))

    class Meta:
        verbose_name = _('Board')
        verbose_name_plural = _('Boards')
